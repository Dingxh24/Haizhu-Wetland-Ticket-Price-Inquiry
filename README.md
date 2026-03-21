# 广州海珠国家湿地公园票价查询（桌面版）

基于 **Flask + pywebview** 的桌面票务辅助系统，附带 PyInstaller 打包脚本。它模拟游客在广州海珠国家湿地公园购票的流程：先判断免票条件，再评估年龄/身份优惠，最后自动应用法定节假日的全票折扣，并在窗口中给出可视化的结果提示。

## 核心功能

- **两段式判断**：第一页勾选免票情形，满足任一条即弹出“您可以享受免票”；否则跳转到第二页再输入年龄、补充优惠条件。
- **年龄/条件优惠规则**：系统自动判定免票（≤6、≥65）和优惠票（7~18、60~64、身高/学生、重度残疾人或陪护），其余全票 20 元。
- **节假日折扣**：通过 `chinese_calendar` 识别五一、国庆、春节；若全票且在假期，自动降为 16 元（8 折），仅作用于全票，不与优惠票叠加。
- **容错性**：年龄表单检查空值、非整数、超过合理范围（0~120）。若未安装 `pywebview`，桌面启动器会退回浏览器模式；若缺少 `chinese_calendar`，节假日折扣保持关闭但不报错。

## 目录结构

```text
wetland_ticket_app/
├─ app.py                         # Flask 后端逻辑
├─ launcher.py                    # 主桌面入口（优先 pywebview）
├─ requirements.txt               # 运行依赖（Flask、pywebview、chinese_calendar 等）
├─ requirements-packaging.txt     # 打包依赖（PyInstaller、图标库等）
├─ wetland_ticket_desktop.spec    # PyInstaller 打包定义
├─ build_windows.bat              # Windows 一键打包脚本
├─ build_macos_linux.sh           # macOS / Linux 打包脚本
├─ assets/
│  ├─ app_icon.png                # 供窗口徽标用的图标（自动注入）
│  └─ app_icon.ico                # Windows 打包用 ICO
├─ templates/
│  ├─ base.html                   # 公共布局（含标题栏、窗口按钮）
│  ├─ index.html                  # 免票判断页
│  ├─ discount.html               # 折扣判断页
│  └─ result.html                 # 结果弹窗页
└─ static/
   ├─ desktop.js                  # 桌面交互（拖拽、窗口按钮）
   └─ style.css                   # 公共样式
```

## 运行方式

### 桌面版（推荐）

```bash
python -m pip install -r requirements.txt
python launcher.py
```

- 如系统安装了 `pywebview` 且支持的后端（默认优先 Qt），程序会以内嵌窗口的形式启动；
- 若 `pywebview` 不可用或运行失败，则自动回退至浏览器模式并提示用户；
- `launcher.py` 会把 Flask 应用绑定到 `127.0.0.1:5000` 并打开桌面窗口，保持原生交互体验。

### 浏览器版（可选）

```bash
python app.py
```

访问 `http://127.0.0.1:5000/` 即可体验完整流程；此方式适用于不愿额外安装 `pywebview` 的环境。

## 打包为可执行文件

### Windows

```bash
python -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
```

或直接运行 `build_windows.bat`，输出 `dist/WetlandTicketDesktop.exe`，其中包含窗口图标、PyInstaller 运行时等。

### macOS / Linux

```bash
python3 -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
```

或执行 `bash build_macos_linux.sh`，生成跨平台的可执行应用。

## 技术说明

- `app.py` 通过 `session` 在免票页与优惠页之间传递状态，避免用户绕过逻辑；
- `calculate_ticket_price` 封装了所有票价规则并返回价格、提示语、原因，方便 `result.html` 界面显示；
- 当 `chinese_calendar` 缺失时，`is_target_holiday` 总是返回 `False`，系统仍然可以正常运行；
- 页面静态资源位于 `static/`，桌面交互脚本负责按钮、拖拽等行为。

## Python 兼容性

- 目标兼容 Python 3.7~3.14；
- 针对不同 pywebview 版本自动调整后端（Windows 上 Python 3.14 默认优先 Qt，若不可用则降级浏览器窗口）；
- 若遇兼容问题，可切换至 Python 3.10/3.11 作为兼容版本。

## 开发与贡献说明

- 项目借助 ChatGPT 5.4、Codex 5.3、Codex 5.1 mini 等 AI 工具辅助编程；
- 仅用于学习与课程设计，不涉及商业用途；
- 欢迎在本地环境中充分测试！

