@echo off

color 04
echo.###      即将开始安装！请勿手勿手动关闭！请勿点击窗口内容！耐心等待！#######
echo.
echo.
echo.
timeout /T 3 /NOBREAK

color 97

C:
CD C:\xiaozhi\MCP\MCP_Windows

pip install -r requirements.txt