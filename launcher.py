import importlib.util
import base64
import inspect
import os
import socket
import sys
import threading
import time
import webbrowser

HOST = '127.0.0.1'
PORT = 5000
URL = f'http://{HOST}:{PORT}/'
APP_TITLE = '广州海珠国家湿地公园票价查询'
WINDOW_WIDTH = 1140
WINDOW_HEIGHT = 780
MIN_WIDTH = 980
MIN_HEIGHT = 700


def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def has_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def show_message(title: str, message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showinfo(title, message)
        root.destroy()
    except Exception:
        print(f'[{title}] {message}')


def wait_for_server(host: str, port: int, timeout: float = 6.0) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def open_browser() -> None:
    webbrowser.open(URL)


def should_prefer_qt_backend() -> bool:
    # On Windows + Python 3.14+, winforms backend may fail due pythonnet ABI gaps.
    return sys.platform.startswith('win') and sys.version_info >= (3, 14)


class WindowApi:
    """
    暴露给前端 JavaScript 的窗口控制 API。
    这些方法会以 window.pywebview.api.xxx() 的形式被网页调用。
    """

    def __init__(self):
        self._main_window = None
        self._is_maximized = False

    def bind_window(self, window):
        self._main_window = window

        def _on_maximized(*_args):
            self._is_maximized = True

        def _on_restored(*_args):
            self._is_maximized = False

        # Older pywebview versions may not expose these events.
        try:
            if hasattr(window, 'events'):
                if hasattr(window.events, 'maximized'):
                    window.events.maximized += _on_maximized
                if hasattr(window.events, 'restored'):
                    window.events.restored += _on_restored
        except Exception:
            pass

    def minimize_window(self):
        if self._main_window is not None:
            self._main_window.minimize()
        return {'ok': True}

    def toggle_maximize(self):
        if self._main_window is None:
            return {'ok': False}

        if self._is_maximized:
            self._main_window.restore()
            self._is_maximized = False
            return {'ok': True, 'maximized': False}

        self._main_window.maximize()
        self._is_maximized = True
        return {'ok': True, 'maximized': True}

    def close_window(self):
        if self._main_window is not None:
            self._main_window.destroy()
        return {'ok': True}

    def get_window_state(self):
        return {'ok': True, 'maximized': self._is_maximized}


class SplashApi:
    """占位：已不再使用独立启动窗。"""


def filter_supported_kwargs(func, kwargs):
    """
    Filter kwargs by callable signature to keep compatibility with
    multiple pywebview versions (3.7-3.14 runtime targets).
    """
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return kwargs

    params = signature.parameters
    for value in params.values():
        if value.kind == inspect.Parameter.VAR_KEYWORD:
            return kwargs

    return {key: value for key, value in kwargs.items() if key in params}


def pick_assets_png_path() -> str:
    assets_dir = resource_path(os.path.join('assets'))
    if not os.path.isdir(assets_dir):
        return ''

    png_files = sorted(
        file_name for file_name in os.listdir(assets_dir) if file_name.lower().endswith('.png')
    )
    if not png_files:
        return ''
    return os.path.join(assets_dir, png_files[0])


def image_data_url(png_path: str) -> str:
    if not png_path or not os.path.exists(png_path):
        return ''
    with open(png_path, 'rb') as file:
        image_base64 = base64.b64encode(file.read()).decode('ascii')
    return f'data:image/png;base64,{image_base64}'


def build_splash_html(icon_data_url: str) -> str:
    icon_html = f"<img src='{icon_data_url}' alt='图标' class='icon-img'>" if icon_data_url else "湿"
    return """<!DOCTYPE html>
<html lang='zh-CN'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>启动中</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Microsoft YaHei','PingFang SC',Arial,sans-serif;background:radial-gradient(circle at top,#1ea56a,#0f5132 70%);color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;overflow:hidden}
.panel{position:relative;width:min(520px,88vw);background:rgba(255,255,255,.10);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.16);border-radius:28px;padding:28px 30px;box-shadow:0 24px 60px rgba(0,0,0,.18)}
.controls{position:absolute;top:14px;right:14px;display:flex;gap:10px}
.ctrl-btn{width:40px;height:40px;border:none;border-radius:12px;background:rgba(255,255,255,.18);color:#0f5132;font-size:18px;font-weight:700;cursor:pointer;transition:background .18s ease,color .18s ease}
.ctrl-btn:hover{background:rgba(255,255,255,.28)}
.ctrl-btn.close:hover{background:#e03131;color:#fff}
.brand{display:flex;gap:16px;align-items:center;margin-bottom:18px}.icon{width:64px;height:64px;border-radius:18px;background:linear-gradient(135deg,#dff8ea,#9fe0be);display:flex;align-items:center;justify-content:center;color:#0f5132;font-weight:800;font-size:30px;box-shadow:0 12px 30px rgba(0,0,0,.16)}
.icon-img{width:100%;height:100%;object-fit:cover;border-radius:inherit;display:block}
.title{font-size:26px;font-weight:800;line-height:1.3;margin:0}.sub{opacity:.9;margin-top:4px}
.loader{height:12px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden;margin:22px 0 14px}.loader span{display:block;height:100%;width:38%;border-radius:999px;background:linear-gradient(90deg,#e7fff1,#bdf0d0);animation:run 1.6s ease-in-out infinite}
@keyframes run{0%{transform:translateX(-120%)}50%{transform:translateX(180%)}100%{transform:translateX(320%)}}
.note{line-height:1.8;opacity:.95;font-size:14px}
</style>
</head>
<body>
    <div class='panel'>
        <div class='controls'>
            <button class='ctrl-btn' id='btnSplashMin'>—</button>
            <button class='ctrl-btn close' id='btnSplashClose'>×</button>
        </div>
        <div class='brand'>
            <div class='icon'>""" + icon_html + """</div>
            <div>
                <h1 class='title'>广州海珠国家湿地公园</h1>
                <div class='sub'>票价查询桌面版正在启动…</div>
            </div>
        </div>
        <div class='loader'><span></span></div>
        <div class='note'>正在连接本地服务并加载桌面界面，请稍候。</div>
    </div>
<script>
function bindSplashControls(){
  const minBtn=document.getElementById('btnSplashMin');
  const closeBtn=document.getElementById('btnSplashClose');
  const callApi=(name)=>{ if(window.pywebview?.api?.[name]) window.pywebview.api[name](); };
  if(minBtn){ minBtn.onclick=(e)=>{e.preventDefault();callApi('minimize_window');}; }
  if(closeBtn){ closeBtn.onclick=(e)=>{e.preventDefault();callApi('close_window');}; }
}
document.addEventListener('DOMContentLoaded', bindSplashControls);
window.addEventListener('pywebviewready', bindSplashControls);
</script>
</body>
</html>"""


def main() -> None:
    if not has_module('flask'):
        show_message(
            '依赖缺失',
            '当前 Python 环境未安装 Flask。\n请先在项目目录执行：\npython -m pip install -r requirements.txt',
        )
        sys.exit(1)

    from app import app

    server_thread = threading.Thread(
        target=lambda: app.run(
            host=HOST,
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True,
        ),
        daemon=True,
    )
    server_thread.start()

    if not wait_for_server(HOST, PORT):
        show_message('启动失败', '本地服务启动超时，请关闭后重试。')
        sys.exit(1)

    if not has_module('webview'):
        show_message(
            '已切换为浏览器模式',
            '未检测到 pywebview，程序将使用默认浏览器打开。\n如需桌面窗口模式，请先执行：\npython -m pip install pywebview',
        )
        threading.Thread(target=open_browser, daemon=True).start()
        server_thread.join()
        return

    import webview

    icon_png = pick_assets_png_path()
    api = WindowApi()

    create_window_kwargs = {
        'js_api': api,
        'width': WINDOW_WIDTH,
        'height': WINDOW_HEIGHT,
        'min_size': (MIN_WIDTH, MIN_HEIGHT),
        'resizable': True,
        'confirm_close': False,
        'frameless': True,
        'easy_drag': False,
        'hidden': False,
        'shadow': True,
        'background_color': '#EDF7F1',
    }

    main_window = webview.create_window(
        APP_TITLE,
        URL,
        **filter_supported_kwargs(webview.create_window, create_window_kwargs),
    )
    api.bind_window(main_window)

    start_kwargs = {}
    if os.path.exists(icon_png):
        start_kwargs['icon'] = icon_png

    if should_prefer_qt_backend():
        start_kwargs['gui'] = 'qt'

    try:
        webview.start(**filter_supported_kwargs(webview.start, start_kwargs))
    except Exception as exc:
        show_message(
            '已切换为浏览器模式',
            '桌面窗口模式启动失败，程序将使用默认浏览器打开。\n'
            '若需桌面窗口，请安装 Qt 后端（示例：python -m pip install PySide6），'
            '或使用 Python 3.13 及以下版本。\n\n'
            f'错误信息：{exc}',
        )
        threading.Thread(target=open_browser, daemon=True).start()
        server_thread.join()


if __name__ == '__main__':
    main()
