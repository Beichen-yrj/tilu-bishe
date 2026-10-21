@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   铁路危货双重预防机制评估系统 - 一键启动
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [失败] 未检测到 python 命令。
  echo 请先安装 Python 3 并勾选 "Add Python to PATH"，然后重新双击本文件。
  echo.
  pause
  exit /b 1
)

python "%~dp0启动项目.py"
if errorlevel 1 (
  echo.
  echo [提示] 启动过程中出现错误，请查看上方信息，或检查：
  echo   · MySQL 是否已启动
  echo   · 数据库是否已初始化（运行 scripts\数据库初始化包\初始化数据库.bat）
  echo   · 前后端依赖是否已安装（pip install -r backend\requirements.txt、cd frontend && npm install）
)

echo.
pause
