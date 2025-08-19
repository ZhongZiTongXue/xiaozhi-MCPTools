@echo off
title Python�ⰲװ����ʹ���пƴ���

:: ���ô�����
setlocal enabledelayedexpansion
set "ERRORS=0"

:: ������ɫ����
set "RED=04"
set "GREEN=0A"
set "YELLOW=0E"
set "BLUE=01"
set "CYAN=03"
set "PURPLE=05"
set "WHITE=07"

:: �����пƴ���Դ
set "MIRROR=-i https://pypi.mirrors.ustc.edu.cn/simple --trusted-host pypi.mirrors.ustc.edu.cn"

:: ������ʱ�ļ��洢���б����и�ʽ��
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

:: ��ʼ��װ
color %RED%
echo.
echo.###      ������ʼ��װ�������ֶ��رմ��ڣ��������������ݣ������ĵȴ���      ###
echo.
timeout /T 6 /NOBREAK

:: ѭ����ȡ��ʱ�ļ��еĿ��б���װ
for /f "usebackq delims=" %%i in ("libraries.tmp") do (
    color %WHITE%
    echo.
    echo.������������������������  ���ڴ��пƴ���װ�⣺%%i  ������������������������
    echo.
    
    :: ���ѡ����ɫ
    set /a "COLOR_INDEX=!RANDOM! %% 6 + 1"
    if !COLOR_INDEX! EQU 1 set "CURRENT_COLOR=%BLUE%"
    if !COLOR_INDEX! EQU 2 set "CURRENT_COLOR=%GREEN%"
    if !COLOR_INDEX! EQU 3 set "CURRENT_COLOR=%CYAN%"
    if !COLOR_INDEX! EQU 4 set "CURRENT_COLOR=%PURPLE%"
    if !COLOR_INDEX! EQU 5 set "CURRENT_COLOR=%YELLOW%"
    if !COLOR_INDEX! EQU 6 set "CURRENT_COLOR=%RED%"
    
    color !CURRENT_COLOR!
    
    :: ִ�а�װ���ʹ���пƴ���
    pip install %%i %MIRROR%
    if !ERRORLEVEL! NEQ 0 (
        echo.��װ�� %%i ʱ����
        set "ERRORS=1"
    )
    echo.
)

:: ɾ����ʱ�ļ�
del /f /q libraries.tmp 2>nul

:: ��װ���
color %WHITE%
echo.
if %ERRORS% EQU 0 (
    color %GREEN%
    echo.#####################       ���п��ļ��ѳɹ���װ       ###################################
) else (
    color %RED%
    echo.#####################       ��װ�����г��ִ���       ###################################
    echo.�������������Ի�ȡ��ϸ��Ϣ
)
echo.
color %WHITE%
echo.#######################       ��װ���򼴽��Զ��˳�       ###################################
echo.
timeout /T 6 /NOBREAK