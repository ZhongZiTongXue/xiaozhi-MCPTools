@echo off


color a
echo.正在准备 下载新版本
echo.
C:
CD C:\xiaozhi\MCP\MCP_Windows\组件\更新服务
Python 下载新版本.py
echo.
echo.正在退出...
timeout /T 6 /NOBREAK

echo.

