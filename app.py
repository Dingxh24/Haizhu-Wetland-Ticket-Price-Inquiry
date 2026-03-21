import os
import sys
from datetime import date
from typing import List, Optional, Tuple

from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for

try:
    import chinese_calendar as calendar
except ImportError:
    calendar = None


def resource_path(relative_path: str) -> str:
    """返回资源文件的绝对路径，兼容开发环境与 PyInstaller 打包环境。"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static'),
)
app.secret_key = 'wetland-ticket-secret-key-2026'

FULL_PRICE = 20
HOLIDAY_FULL_PRICE = 16
DISCOUNT_PRICE = 10

FREE_OPTIONS = {
    'child_free': '6周岁（含6周岁）以下儿童，或身高1.2米（含1.2米）以下儿童',
    'senior_free': '65周岁（含65周岁）以上老人（持有效证件）',
    'special_free': '现役军人、军队离退休干部、残疾人、最低生活保障对象、特困人员、本市户籍享受抚恤补助的优抚对象（持有效证件）',
    'none': '以上均不符合',
}

DISCOUNT_OPTIONS = {
    'student_or_height': '因身高或学生身份符合优惠票：1.2米以上且1.5米及以下儿童；或全日制本科及以下学历学生',
    'special_discount': '盲人、智力残疾人、双下肢残疾人、其他重度残疾人，或其1名陪护人员（持有效证件）',
}


def pick_assets_png_name() -> str:
    assets_dir = resource_path('assets')
    icon_name = 'Haizhu_Wetland_app_icon.png'
    icon_path = os.path.join(assets_dir, icon_name)
    return icon_name if os.path.isfile(icon_path) else ''


def is_target_holiday(check_date: Optional[date] = None) -> bool:
    """
    判断当天是否属于“五一 / 国庆 / 春节”法定假期。
    返回 True 时，单次购买全票按 8 折，即 16 元。
    这里只对全票生效；优惠票、免票不再叠加该折扣。
    """
    if check_date is None:
        check_date = date.today()

    if calendar is None:
        return False

    on_holiday, holiday_name = calendar.get_holiday_detail(check_date)
    return on_holiday and holiday_name in {'劳动节', '国庆节', '春节'}


def calculate_ticket_price(age: int, selected_discount_options: List[str]) -> Tuple[int, str, str]:
    """
    根据年龄和用户勾选的优惠条件计算票价。
    返回 (price, message, reason)
    """
    if age <= 6:
        return 0, '您可以享受免票', f'年龄为 {age} 岁，符合 6 周岁及以下免票条件。'

    if age >= 65:
        return 0, '您可以享受免票', f'年龄为 {age} 岁，符合 65 周岁及以上免票条件。'

    reasons: List[str] = []

    if 6 < age <= 18:
        reasons.append(f'年龄为 {age} 岁，符合 6 周岁以上至 18 周岁优惠票条件')

    if 60 <= age <= 64:
        reasons.append(f'年龄为 {age} 岁，符合 60~64 周岁优惠票条件')

    if 'student_or_height' in selected_discount_options:
        reasons.append('已勾选“身高或学生身份符合优惠票”条件')

    if 'special_discount' in selected_discount_options:
        reasons.append('已勾选“重度残疾人或陪护人员优惠票”条件')

    if reasons:
        return DISCOUNT_PRICE, f'您的票价是{DISCOUNT_PRICE}元', '；'.join(reasons) + '。'

    if is_target_holiday():
        return HOLIDAY_FULL_PRICE, f'您的票价是{HOLIDAY_FULL_PRICE}元', '不符合免票和优惠票条件，按全票处理；当前为五一/国庆/春节假期，全票自动按 8 折。'

    return FULL_PRICE, f'您的票价是{FULL_PRICE}元', '不符合免票和优惠票条件，按普通全票处理。'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', free_options=FREE_OPTIONS, error='')


@app.route('/assets/<path:filename>', methods=['GET'])
def asset_file(filename: str):
    return send_from_directory(resource_path('assets'), filename)


@app.context_processor
def inject_asset_icon():
    app_mark_icon = pick_assets_png_name()
    app_mark_icon_url = url_for('asset_file', filename=app_mark_icon) if app_mark_icon else ''
    return {'app_mark_icon_url': app_mark_icon_url}


@app.route('/submit-free', methods=['POST'])
def submit_free():
    selected_free_options = request.form.getlist('free_options')

    if not selected_free_options:
        return render_template(
            'index.html',
            free_options=FREE_OPTIONS,
            error='请先选择一项免票情况，或选择“以上均不符合”。',
        )

    if 'none' in selected_free_options and len(selected_free_options) > 1:
        return render_template(
            'index.html',
            free_options=FREE_OPTIONS,
            error='“以上均不符合”不能和其他免票选项同时勾选。',
        )

    if 'none' not in selected_free_options:
        session.pop('passed_free_check', None)
        return render_template('result.html', message='您可以享受免票', reason='已勾选免票条件，因此可直接享受免票。')

    session['passed_free_check'] = True
    return redirect(url_for('discount_page'))


@app.route('/discount', methods=['GET'])
def discount_page():
    if not session.get('passed_free_check'):
        return redirect(url_for('index'))

    return render_template(
        'discount.html',
        discount_options=DISCOUNT_OPTIONS,
        error='',
        holiday_active=is_target_holiday(),
        full_price=FULL_PRICE,
        holiday_full_price=HOLIDAY_FULL_PRICE,
        discount_price=DISCOUNT_PRICE,
    )


@app.route('/submit-discount', methods=['POST'])
def submit_discount():
    if not session.get('passed_free_check'):
        return redirect(url_for('index'))

    age_text = request.form.get('age', '').strip()
    selected_discount_options = request.form.getlist('discount_options')

    if not age_text:
        return render_template(
            'discount.html',
            discount_options=DISCOUNT_OPTIONS,
            error='请输入年龄。',
            holiday_active=is_target_holiday(),
            full_price=FULL_PRICE,
            holiday_full_price=HOLIDAY_FULL_PRICE,
            discount_price=DISCOUNT_PRICE,
        )

    try:
        age = int(age_text)
    except ValueError:
        return render_template(
            'discount.html',
            discount_options=DISCOUNT_OPTIONS,
            error='年龄必须是整数。',
            holiday_active=is_target_holiday(),
            full_price=FULL_PRICE,
            holiday_full_price=HOLIDAY_FULL_PRICE,
            discount_price=DISCOUNT_PRICE,
        )

    if age < 0 or age > 120:
        return render_template(
            'discount.html',
            discount_options=DISCOUNT_OPTIONS,
            error='请输入合理的年龄（0~120）。',
            holiday_active=is_target_holiday(),
            full_price=FULL_PRICE,
            holiday_full_price=HOLIDAY_FULL_PRICE,
            discount_price=DISCOUNT_PRICE,
        )

    price, message, reason = calculate_ticket_price(age, selected_discount_options)
    session.pop('passed_free_check', None)
    return render_template('result.html', message=message, price=price, reason=reason)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
