@echo off


color a
echo.正在准备 向服务器登记用户.
echo.
C:
CD C:\xiaozhi\MCP\MCP_Windows\组件\登记服务
Python 向服务器登记用户.py
echo.
echo.正在退出...
timeout /T 6 /NOBREAK

echo.

