@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem 真正的启动逻辑在 scripts\启动项目.py（前后端分别位于 frontend/、backend/）
python "%~dp0scripts\启动项目.py" %*
if errorlevel 1 (
  echo.
  echo [提示] 启动失败，请查看上方信息；详细排查见 docs\设计\项目开发说明.md
  pause
)
