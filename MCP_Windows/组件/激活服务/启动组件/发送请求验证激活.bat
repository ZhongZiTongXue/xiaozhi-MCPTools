@echo off


color a
echo.正在准备 发送请求验证激活
echo.
C:
CD C:\xiaozhi\MCP\MCP_Windows\组件\激活服务
Python 发送请求验证激活.py
echo.
echo.正在退出...
timeout /T 6 /NOBREAK

echo.

