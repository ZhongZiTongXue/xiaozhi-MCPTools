@echo off
title Python库安装程序（使用中科大镜像）

:: 设置错误处理
setlocal enabledelayedexpansion
set "ERRORS=0"

:: 定义颜色变量
set "RED=04"
set "GREEN=0A"
set "YELLOW=0E"
set "BLUE=01"
set "CYAN=03"
set "PURPLE=05"
set "WHITE=07"

:: 定义中科大镜像源
set "MIRROR=-i https://pypi.mirrors.ustc.edu.cn/simple --trusted-host pypi.mirrors.ustc.edu.cn"

:: 创建临时文件存储库列表（竖列格式）
echo websockets> libraries.tmp
echo python-dotenv>> libraries.tmp
echo fastmcp>> libraries.tmp
echo pyautogui>> libraries.tmp
echo pyperclip>> libraries.tmp
echo mcp>> libraries.tmp
echo paho-mqtt>> libraries.tmp
echo requests>> libraries.tmp
echo beautifulsoup4>> libraries.tmp
echo pycaw>> libraries.tmp
echo psutil>> libraries.tmp

:: 开始安装
color %RED%
echo.
echo.###      即将开始安装！请勿手动关闭窗口！请勿点击窗口内容！请耐心等待！      ###
echo.
timeout /T 6 /NOBREAK

:: 循环读取临时文件中的库列表并安装
for /f "usebackq delims=" %%i in ("libraries.tmp") do (
    color %WHITE%
    echo.
    echo.————————————  正在从中科大镜像安装库：%%i  ————————————
    echo.
    
    :: 随机选择颜色
    set /a "COLOR_INDEX=!RANDOM! %% 6 + 1"
    if !COLOR_INDEX! EQU 1 set "CURRENT_COLOR=%BLUE%"
    if !COLOR_INDEX! EQU 2 set "CURRENT_COLOR=%GREEN%"
    if !COLOR_INDEX! EQU 3 set "CURRENT_COLOR=%CYAN%"
    if !COLOR_INDEX! EQU 4 set "CURRENT_COLOR=%PURPLE%"
    if !COLOR_INDEX! EQU 5 set "CURRENT_COLOR=%YELLOW%"
    if !COLOR_INDEX! EQU 6 set "CURRENT_COLOR=%RED%"
    
    color !CURRENT_COLOR!
    
    :: 执行安装命令（使用中科大镜像）
    pip install %%i %MIRROR%
    if !ERRORLEVEL! NEQ 0 (
        echo.安装库 %%i 时出错！
        set "ERRORS=1"
    )
    echo.
)

:: 删除临时文件
del /f /q libraries.tmp 2>nul

:: 安装结果
color %WHITE%
echo.
if %ERRORS% EQU 0 (
    color %GREEN%
    echo.#####################       所有库文件已成功安装       ###################################
) else (
    color %RED%
    echo.#####################       安装过程中出现错误       ###################################
    echo.请检查上面的输出以获取详细信息
)
echo.
color %WHITE%
echo.#######################       安装程序即将自动退出       ###################################
echo.
timeout /T 6 /NOBREAK