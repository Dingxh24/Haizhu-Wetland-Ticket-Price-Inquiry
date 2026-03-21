import importlib.util
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


def wait_for_server(host: str, port: int, timeout: float = 15.0) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def open_browser() -> None:
    webbrowser.open(URL)


class WindowApi:
    """
    暴露给前端 JavaScript 的窗口控制 API。
    这些方法会以 window.pywebview.api.xxx() 的形式被网页调用。
    """

    def __init__(self):
        self.main_window = None
        self.is_maximized = False

    def bind_window(self, window):
        self.main_window = window

        def _on_maximized(*_args):
            self.is_maximized = True

        def _on_restored(*_args):
            self.is_maximized = False

        window.events.maximized += _on_maximized
        window.events.restored += _on_restored

    def minimize_window(self):
        if self.main_window is not None:
            self.main_window.minimize()
        return {'ok': True}

    def toggle_maximize(self):
        if self.main_window is None:
            return {'ok': False}

        if self.is_maximized:
            self.main_window.restore()
            self.is_maximized = False
            return {'ok': True, 'maximized': False}

        self.main_window.maximize()
        self.is_maximized = True
        return {'ok': True, 'maximized': True}

    def close_window(self):
        if self.main_window is not None:
            self.main_window.destroy()
        return {'ok': True}

    def get_window_state(self):
        return {'ok': True, 'maximized': self.is_maximized}


def build_splash_html() -> str:
    return """<!DOCTYPE html>
<html lang='zh-CN'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>启动中</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:'Microsoft YaHei','PingFang SC',Arial,sans-serif;background:radial-gradient(circle at top,#1ea56a,#0f5132 70%);color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;overflow:hidden}
.panel{width:min(520px,88vw);background:rgba(255,255,255,.10);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.16);border-radius:28px;padding:28px 30px;box-shadow:0 24px 60px rgba(0,0,0,.18)}
.brand{display:flex;gap:16px;align-items:center;margin-bottom:18px}.icon{width:64px;height:64px;border-radius:18px;background:linear-gradient(135deg,#dff8ea,#9fe0be);display:flex;align-items:center;justify-content:center;color:#0f5132;font-weight:800;font-size:30px;box-shadow:0 12px 30px rgba(0,0,0,.16)}
.title{font-size:26px;font-weight:800;line-height:1.3;margin:0}.sub{opacity:.9;margin-top:4px}
.loader{height:12px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden;margin:22px 0 14px}.loader span{display:block;height:100%;width:38%;border-radius:999px;background:linear-gradient(90deg,#e7fff1,#bdf0d0);animation:run 1.6s ease-in-out infinite}
@keyframes run{0%{transform:translateX(-120%)}50%{transform:translateX(180%)}100%{transform:translateX(320%)}}
.note{line-height:1.8;opacity:.95;font-size:14px}.tag{display:inline-block;margin-top:10px;padding:8px 12px;border-radius:999px;background:rgba(255,255,255,.14);font-size:13px}
</style>
</head>
<body>
    <div class='panel'>
        <div class='brand'>
            <div class='icon'>湿</div>
            <div>
                <h1 class='title'>广州海珠国家湿地公园</h1>
                <div class='sub'>票价查询桌面版正在启动…</div>
            </div>
        </div>
        <div class='loader'><span></span></div>
        <div class='note'>正在连接本地服务并加载桌面界面，请稍候。<br>窗口启动后将显示原生感标题栏、最小化 / 最大化 / 关闭按钮，以及欢迎页过渡效果。</div>
        <div class='tag'>Wetland Ticket Desktop</div>
    </div>
</body>
</html>"""


def main() -> None:
    if not has_module('flask'):
        show_message(
            '依赖缺失',
            '当前 Python 环境未安装 Flask。\n请先在项目目录执行：\npython -m pip install -r requirements.txt',
        )
        sys.exit(1)

    from app import app, resource_path

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

    icon_png = resource_path(os.path.join('assets', 'app_icon.png'))
    api = WindowApi()
    main_loaded = threading.Event()

    main_window = webview.create_window(
        APP_TITLE,
        URL,
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(MIN_WIDTH, MIN_HEIGHT),
        resizable=True,
        confirm_close=False,
        frameless=True,
        easy_drag=False,
        hidden=True,
        shadow=True,
        background_color='#EDF7F1',
    )
    api.bind_window(main_window)

    def on_loaded(*_args):
        main_loaded.set()

    main_window.events.loaded += on_loaded

    splash_window = webview.create_window(
        '启动中',
        html=build_splash_html(),
        width=640,
        height=420,
        resizable=False,
        frameless=True,
        easy_drag=True,
        on_top=True,
        background_color='#0F5132',
    )

    def after_start():
        main_loaded.wait(timeout=8)
        time.sleep(0.7)
        try:
            splash_window.destroy()
        except Exception:
            pass
        main_window.show()

    start_kwargs = {}
    if os.path.exists(icon_png):
        start_kwargs['icon'] = icon_png

    webview.start(after_start, **start_kwargs)


if __name__ == '__main__':
    main()
