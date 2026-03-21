# 广州海珠国家湿地公园票价查询（桌面版）

这是一个基于 **Flask + pywebview** 的本地桌面票价查询程序。
有 PyInstaller 打包支持。

## 运行方法
```bash
python -m pip install -r requirements.txt
python launcher.py
```

## 打包方法
```bash
python -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
```
