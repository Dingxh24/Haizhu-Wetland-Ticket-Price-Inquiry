@echo off
cd /d %~dp0
python -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
pause
