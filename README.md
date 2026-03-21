# 广州海珠国家湿地公园票价查询（原生感桌面版）

这是一个基于 **Flask + pywebview** 的本地桌面票价查询程序。

## 本次升级内容
- 使用 frameless 窗口，隐藏系统浏览器地址栏；
- 增加自定义顶部标题栏；
- 增加最小化 / 最大化 / 关闭按钮；
- 增加启动欢迎页（Splash Screen）；
- 保留原有免票 / 优惠票 / 节假日折扣逻辑；
- 保留 PyInstaller 打包支持。

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
