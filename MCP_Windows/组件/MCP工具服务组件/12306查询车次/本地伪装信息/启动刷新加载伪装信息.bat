@echo off


color a
C:
CD C:\xiaozhi\MCP\MCP_Windows\组件\MCP工具服务组件\12306查询车次\本地伪装信息
Python 刷新加载伪装信息.py


echo.获取车票伪装信息刷新完成！

timeout /T 6 /NOBREAK