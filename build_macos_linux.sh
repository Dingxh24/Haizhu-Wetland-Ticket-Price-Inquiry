#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m pip install -r requirements-packaging.txt
pyinstaller --clean wetland_ticket_desktop.spec
