# 广州海珠国家湿地公园票价查询（桌面版）

这是一个基于 **Flask + pywebview** 并有 PyInstaller 打包支持的本地桌面票价查询程序。
## 1. 功能说明

### 第一页：免票判断

- 用户先勾选是否符合免票条件。
- 只要勾选了任意一个免票条件，点击“查询”后直接弹出：**您可以享受免票**。
- 如果用户选择“以上均不符合”，则进入第二页。
- “以上均不符合”与其他免票选项互斥。

### 第二页：年龄 + 优惠票判断

- 用户输入年龄。
- 可额外勾选优惠票条件，也可以不勾选。
- 系统根据年龄和优惠条件自动判断：
  - 6周岁及以下：免票
  - 65周岁及以上：免票
  - 6周岁以上至18周岁（含18周岁）：优惠票 10 元
  - 60至64周岁（含64周岁）：优惠票 10 元
  - 其他符合补充优惠条件者：优惠票 10 元
  - 其余情况：全票 20 元

### 节假日自动折扣

- 在 **五一 / 国庆 / 春节** 假期内：
  - 若用户应购买全票，则自动按 **8 折** 显示 **16 元**。
- 该折扣只作用于全票，不与优惠票叠加。

## 2. 项目结构

```text
wetland_ticket_app/
├─ app.py                         # Flask 主程序
├─ launcher.py                    # 桌面窗口启动器（优先 pywebview）
├─ requirements.txt               # 运行依赖
├─ requirements-packaging.txt     # 打包依赖
├─ wetland_ticket_desktop.spec    # PyInstaller 打包配置
├─ build_windows.bat              # Windows 一键打包脚本
├─ build_macos_linux.sh           # macOS / Linux 打包脚本
├─ assets/
│  ├─ app_icon.png                # 桌面窗口图标
│  └─ app_icon.ico                # Windows 打包图标
├─ templates/
│  ├─ index.html                  # 免票页
│  ├─ discount.html               # 优惠票页
│  └─ result.html                 # 结果弹窗页
└─ static/
   └─ style.css                   # 页面样式
```

## 3. 如何运行

### 方式 A：直接运行桌面版

```bash
python -m pip install -r requirements.txt
python launcher.py
```

运行后：

- 如果已安装 `pywebview`，程序会以 **桌面窗口** 打开；
- 如果未安装 `pywebview`，程序会自动退回浏览器模式。

### 方式 B：只运行网页版

```bash
python app.py
```

然后访问：

```text
http://127.0.0.1:5000/
```

## 4. 如何打包为 exe

### Windows

```bash
python -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
```

生成文件位于：

```text
dist/WetlandTicketDesktop.exe
```

也可以直接双击：

```text
build_windows.bat
```

### macOS / Linux

```bash
python3 -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
```

或直接执行：

```bash
bash build_macos_linux.sh
```
## 6. Python 兼容范围
- 目标兼容：Python 3.7 - 3.14；
- 已通过依赖分流与运行时参数兼容处理，自动适配不同版本 pywebview 的 API 差异。
- Windows + Python 3.14 默认优先尝试 Qt 后端（如 `PySide6`）。若不可用，会自动降级为浏览器模式，不会崩溃退出。
- 如果遇到Python版本不兼容问题，可以通过安装并使用Python3.10或3.11解决

## 5. 项目来源说明

本项目在设计与开发过程中，使用了包括Chat-GPT 5.4，Codex5.1 mini Codex5.3等 AI 工具辅助编程。


## 6. 声明

本项目仅用于学习与课程设计，不涉及商业用途。

