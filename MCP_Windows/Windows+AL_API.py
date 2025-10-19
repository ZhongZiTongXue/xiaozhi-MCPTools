from mcp.server.fastmcp import FastMCP
import logging
import subprocess
import webbrowser
import math
import random
import ctypes
import sys
import os
import requests
from bs4 import BeautifulSoup

# -------------------------------------------------------------------------------------------------
# 配置编码和日志
# 确保输出和日志使用正确的编码，避免中文字符显示问题
if sys.stderr.reconfigure(encoding='utf-8'):
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Windows_MCP_Tools')
# -------------------------------------------------------------------------------------------------

# 创建MCP服务器实例
mcp = FastMCP("WindowsToos")

# -------------------------------------------------------------------------------------------------
# 获取当前脚本所在的目录
# 这样可以确保我们能够正确找到预设文件，而无需手动指定绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建预设文件的完整路径
# 假设预设文件位于当前目录下的"预设"子文件夹中
programs_file_path = os.path.join(current_dir, "预设", "程序预设.txt")
commands_file_path = os.path.join(current_dir, "预设", "命令预设.txt")

# 构建token文件的完整路径
token_file_path = os.path.join(current_dir, "数据", "接入API", "Token.txt")
# -------------------------------------------------------------------------------------------------

# 读取预设文件
def load_presets(file_path: str) -> dict:
    """
    从指定的文本文档中加载预设信息。
    参数： file_path: 文本文档的路径
    """
    presets = {}
    try:
        if not os.path.exists(file_path):  # 检查文件是否存在
            logger.info(f"\n未找到预设文件！已创建并写入默认内容")
            # 确保文件所在目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # 创建文件并写入默认内容
            default_content = get_default_content(file_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(default_content)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    # 分割键值对，格式为 "键=值"
                    key, value = line.split('=', 1)
                    presets[key] = value
        return presets
    except Exception as e:
        logger.error(f"读取预设文件 {file_path} 时出错: {str(e)}")
        return {}

def get_default_content(file_path: str) -> str:
    """
    根据文件路径返回对应的默认内容。
    参数： file_path: 文本文档的路径
    """
    if "程序预设.txt" in file_path:
        return """记事本=C:\\Windows\\System32\\notepad.exe
计算器=C:\\Windows\\System32\\calc.exe
"""
    elif "命令预设.txt" in file_path:
        return """IP配置=ipconfig
系统信息=systeminfo
网络状态=netstat -ano
锁定电脑=rundll32.exe user32.dll,LockWorkStation
"""
    else:
        return ""

# 加载预设
preset_programs = load_presets(programs_file_path)
preset_commands = load_presets(commands_file_path)

# 读取token
def load_token(file_path: str) -> str:
    """
    从指定的文本文档中加载token。
    参数： file_path: 文本文档的路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
            return token
    except FileNotFoundError:
        logger.error(f"token文件 {file_path} 未找到")
        return ""
    except Exception as e:
        logger.error(f"读取token文件 {file_path} 时出错: {str(e)}")
        return ""

# 加载token
token = load_token(token_file_path)
# -------------------------------------------------------------------------------------------------


# 添加一个计算器工具
@mcp.tool()
def 计算器(python_expression: str) -> dict:
    """
    用于数学计算时，请始终使用此工具来计算 Python 表达式的结果。
    可以使用 `math` 和 `random` 模块。
    """
    result = eval(python_expression)
    logger.info(f"计算公式：{python_expression}，结果：{result}")
    return {"是否成功": True, "结果": result}

# -------------------------------------------------------------------------------------------------

# 定义工具函数：运行电脑端程序
@mcp.tool()
def 运行电脑端软件文件或程序(program_name: str) -> dict:
    """
    运行预设程序或指定路径的程序
    参数： program_name: 程序名称或路径，例如 "记事本" 或 "C:\\Windows\\System32\\notepad.exe"
    """
    try:
        # 如果是预设程序名称，则获取对应的路径
        program_path = preset_programs.get(program_name, program_name)
        if program_path.endswith('.lnk'):
            # 如果是.lnk文件，使用os.startfile打开
            os.startfile(program_path)
        else:
            # 否则直接运行程序
            subprocess.Popen(program_path)
        logger.info(f"\n\n运行程序：{program_path}\n")
        return {"是否成功": True, "结果": f"程序已启动：{program_path}"}
    except Exception as e:
        logger.error(f"\n\n错误！程序: {program_name} 运行失败！: {str(e)}\n")
        return {"是否成功": False, "错误请检查路径": str(e)}

# -------------------------------------------------------------------------------------------------

# 定义工具函数：在电脑上打开URL网址
@mcp.tool()
def 在电脑上打开URL网址(url: str) -> dict:
    """
    打开指定URL的网页。在电脑的浏览器上
    参数： url: 网页URL，例如 "https://www.baidu.com"
    """
    try:
        webbrowser.open(url)
        logger.info(f"\n\n执行打开URL网页: {url}\n")
        return {"是否成功": True, "结果": f"网页已打开：{url}"}
    except Exception as e:
        logger.error(f"错误！网页 {url} 打开失败！: {str(e)}\n")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------


# 定义工具函数：在电脑上运行CMD指令
@mcp.tool()
def 在电脑上运行CMD命令(command_name: str) -> dict:
    """
    运行预设CMD指令或指定的CMD指令。控制查看操作电脑信息/状态/锁定电脑等
    参数：command_name: CMD指令名称或命令，例如 "IP配置" 或 "ipconfig"
    """
    try:
        # 如果是预设指令名称，则获取对应的命令
        command = preset_commands.get(command_name, command_name)
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        logger.info(f"\n\n执行 CMD 命令: {command}\n执行结果: {output}\n")

        return {"是否成功": True, "结果": f"命令执行成功：\n{output}"}
    except Exception as e:
        logger.error(f"错误！运行 CMD 命令：{command_name} 失败！: {str(e)}\n")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------

# 定义工具函数：创建文件写入内容
@mcp.tool()
def 在电脑上创建文件与入内容(file_path: str, content: str) -> dict:
    """
    在指定路径创建文件并写入内容
    参数： file_path: 文件路径，例如 "C:\\小智创建的文件.txt"
    参数： content: 要写入的内容
    桌面路径可以用调用工具 在电脑上执行CMD指令 查看本电脑具体完整桌面路径
    """
    try:
        # 确保文件路径的目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 打开文件并写入内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"\n\n文件创建并写入成功：{file_path}\n内容：{content}\n")
        return {"是否成功": True, "结果": f"文件已创建并写入成功：{file_path}"}
    except Exception as e:
        logger.error(f"创建文件并写入内容失败：{str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------


# 定义工具函数：读取复制内容
@mcp.tool()
def 读取复制内容() -> dict:
    """
    读取计算机中复制的内容，比如复制题目，复制文字文本等
    """
    try:
        # 导入tkinter模块来处理剪贴板
        import tkinter as tk
        
        # 创建一个Tkinter根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 从剪贴板读取内容
        clipboard_content = root.clipboard_get()
        
        # 销毁窗口
        root.destroy()
        
        logger.info(f"\n\n从剪贴板读取到内容: {clipboard_content}\n")
        
        return {"是否成功": True, "结果": clipboard_content}
    except Exception as e:
        logger.error(f"读取剪贴板内容失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------

import pyautogui
import pyperclip
import time

# 定义工具函数：自动粘贴内容到当前光标位置
@mcp.tool()
def 写入填入一段内容(content: str) -> dict:
    """
    写入填入将指定内容复制到剪贴板，然后模拟 Ctrl+V 操作粘贴到当前光标所在位置。不进行回车发送
    参数：
    content: 要粘贴的内容，例如 "这是有小智填入的一段内容！"
    """
    try:
        # 复制内容到剪贴板
        pyperclip.copy(content)

        # 等待1秒，确保目标窗口已准备好
        time.sleep(1)

        # 模拟 Ctrl+V 操作粘贴内容
        pyautogui.hotkey('Ctrl', 'v')

        logger.info(f"\n\n已将内容复制到剪贴板并粘贴到当前光标位置: {content}\n")
        return {"是否成功": True, "结果": f"已成功复制并粘贴内容: {content}"}
    except Exception as e:
        logger.error(f"自动粘贴内容失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# 定义工具函数：回车发送一段内容
@mcp.tool()
def 回车发送() -> dict:
    """
    模拟按下回车发送当前输入框中的内容
    """
    try:

        # 模拟 Enter 操作发送内容

        pyautogui.hotkey('Enter')
        
        logger.info(f"\n\n已模拟按下回车发送\n")
        return {"是否成功": True, "结果": f"已模拟按下回车发送！"}
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}


# -------------------------------------------------------------------------------------------------



# 定义工具函数：回车发送一段内容
@mcp.tool()
def 撤销操作() -> dict:
    """
    模拟按下Ctrl+Z 撤销刚刚的操作！
    比如刚刚填充的内容
    """
    try:

        # 模拟 Ctrl+Z 操作粘贴内容
        pyautogui.hotkey('Ctrl', 'z')
        
        logger.info(f"\n\n已模拟按下撤销快捷键！\n")
        return {"是否成功": True, "结果": f"已模拟按下撤销快捷键！"}
    except Exception as e:
        logger.error(f"撤销操作失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}


# -------------------------------------------------------------------------------------------------




import subprocess

# 定义工具函数：锁定电脑
@mcp.tool()
def 锁定电脑() -> dict:
    """
    锁定当前 Windows 计算机
    调用方法：锁定电脑({})
    """
    try:
        # 使用 subprocess 调用命令锁定电脑
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True, check=True)
        logger.info("\n\n电脑已锁定\n")
        return {"是否成功": True, "结果": "电脑已锁定"}
    except Exception as e:
        logger.error(f"锁定电脑失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}


# -------------------------------------------------------------------------------------------------


# 定义工具函数：Shutdown系统操作（关机、重启、注销等）
@mcp.tool()
def 电脑关机计划(操作类型: str, 延迟时间: int = 0) -> dict:
    """
    执行Shutdown电脑关机计划操作，如关机、重启、等，或 取消已计划的操作。
    支持延时执行。
    参数：
    操作类型: 操作类型，可以是 "关机"、"重启" 或 "取消"
    延迟时间: 操作前的延迟时间（秒），默认为0（立即执行）。仅在操作类型不是"取消"时有效
    调用时需要向用户确认，以免关机导致数据丢失
    """
    try:
        # 映射操作类型到 shutdown 参数
        operation_map = {
            "关机": "/s",
            "重启": "/r",
            "取消": "/a"
        }

        # 获取对应的 shutdown 参数
        operation_param = operation_map.get(操作类型)
        if not operation_param:
            return {"是否成功": False, "错误": f"不支持的操作类型: {操作类型}"}

        if 操作类型 == "取消":
            # 取消操作
            subprocess.run(f"shutdown {operation_param}", shell=True, check=True)
            logger.info("\n\n已取消计划的系统操作\n")
            return {"是否成功": True, "结果": "已取消计划的系统操作"}
        else:
            # 构建命令
            command = f"shutdown {operation_param} /t {延迟时间}"

            # 执行命令
            subprocess.run(command, shell=True, check=True)

            logger.info(f"\n\n已计划系统操作：{操作类型}，延迟：{延迟时间}秒\n")
            return {"是否成功": True, "结果": f"已计划系统操作：{操作类型}，延迟：{延迟时间}秒"}
    except Exception as e:
        logger.error(f"执行系统操作失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
import ctypes

@mcp.tool()
def 设置主人电脑系统的音量(params: dict) -> dict:
    """
    设置 Windows 系统的音量
    调用方法：设置电脑音量({"音量": 50})  # 音量范围为 0-100
    """
    try:
        # 从参数中获取音量值，如果不存在则默认为50
        volume = params.get("音量", 50)
        
        # 确保音量值在0-100范围内
        if not 0 <= volume <= 100:
            return {"是否成功": False, "错误": "音量值必须在0-100之间"}
        
        # 获取音频设备
        devices = AudioUtilities.GetSpeakers()
        # 激活音量控制接口
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None
        )
        volume_control = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        
        # 设置音量
        volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)
        
        logger.info(f"\n\n电脑音量已设置为: {volume}%\n")
        return {"是否成功": True, "结果": f"电脑音量已设置为: {volume}%"}
    except Exception as e:
        logger.error(f"设置电脑音量失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}
# -------------------------------------------------------------------------------------------------

@mcp.tool()
def 调用系统截图工具(screenshot_type: str) -> dict:
    """
    调用系统的截图工具
    参数：
    screenshot_type: 截图类型，"全屏" 或 "区域"
    """
    try:
        import pyautogui
        # 模拟按键：Print Screen（区域截图）或 Alt+Print Screen（全屏截图）
        if screenshot_type == "全屏":
            pyautogui.hotkey('alt', 'printscreen')
            action_text = "全屏截屏"
        elif screenshot_type == "区域":
            pyautogui.hotkey('printscreen')
            action_text = "区域截屏"
        else:
            return {"是否成功": False, "错误": "无效的截图类型，仅支持 '全屏' 或 '区域'"}

        logger.info(f"\n\n已调用系统 {action_text} 工具，截图将保存到剪贴板！\n")
        return {"是否成功": True, "结果": f"已调用系统 {action_text} 工具，截图将保存到剪贴板！"}
    except Exception as e:
        logger.error(f"调用系统截图工具失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------

@mcp.tool()
def 显示电脑桌面() -> dict:
    """
    模拟按下 Win+D 组合键，显示桌面
    """
    try:
        import pyautogui
        pyautogui.hotkey('winleft', 'd')  # 模拟按下 Win+D 组合键
        logger.info("\n\n已调用 Win+D 返回桌面\n")
        return {"是否成功": True, "结果": "已按下 Win+D 返回桌面"}
    except Exception as e:
        logger.error(f"返回桌面失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}
    
# -------------------------------------------------------------------------------------------------

import psutil
import time

@mcp.tool()
def 查看系统资源使用情况() -> dict:
    """
    查看系统资源使用情况，包括CPU、内存、磁盘、和网络使用情况
    """
    try:
        # 获取 CPU 使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 获取所有磁盘分区的使用情况
        disk_partitions = psutil.disk_partitions()
        disk_usages = []
        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usages.append(f"{partition.device}: {usage.percent}% 已使用")
            except:
                disk_usages.append(f"{partition.device}: 无法获取使用情况")
        
        # 获取网络吞吐量
        net_io_before = psutil.net_io_counters()
        time.sleep(1)
        net_io_after = psutil.net_io_counters()
        upload_speed = (net_io_after.bytes_sent - net_io_before.bytes_sent) / 1024  # KB/s
        download_speed = (net_io_after.bytes_recv - net_io_before.bytes_recv) / 1024  # KB/s
        
        # 构建结果字符串
        result = (
            f"CPU使用率: {cpu_usage}%\n"
            f"内存使用率: {memory_usage}%\n"
            f"磁盘使用情况: {', '.join(disk_usages)}\n"
            f"网络上传速度: {upload_speed:.2f} KB/s\n"
            f"网络下载速度: {download_speed:.2f} KB/s"
        )
        
        logger.info(f"\n\n系统资源使用情况：\n{result}\n")
        return {"是否成功": True, "结果": result}
    except Exception as e:
        logger.error(f"查看系统资源使用情况失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------


import subprocess


@mcp.tool()
def 查看电脑配置信息() -> dict:
    """
    查看电脑的配置信息，使用 CMD 命令获取详细信息
    """
    try:
        # 获取系统信息
        system_info = subprocess.check_output("systeminfo", shell=True, text=True, errors="replace")
        
        # 获取 CPU 信息
        cpu_info = subprocess.check_output("wmic cpu get name", shell=True, text=True, errors="replace").strip()
        
        # 获取内存信息
        ram_info = subprocess.check_output("wmic memorychip get capacity", shell=True, text=True, errors="replace").strip()
        
        # 获取主板信息
        motherboard_info = subprocess.check_output("wmic baseboard get manufacturer,model", shell=True, text=True, errors="replace").strip()
        
        # 获取磁盘信息
        disk_info = subprocess.check_output("wmic diskdrive get model,size", shell=True, text=True, errors="replace").strip()
        
        # 获取 GPU 信息
        gpu_info = subprocess.check_output("wmic path win32_videocontroller get name", shell=True, text=True, errors="replace").strip()
        
        # 构建结果字符串
        result = (
            f"系统信息：\n{system_info}\n\n"
            f"CPU 信息：\n{cpu_info}\n\n"
            f"内存信息：\n{ram_info}\n\n"
            f"主板信息：\n{motherboard_info}\n\n"
            f"磁盘信息：\n{disk_info}\n\n"
            f"GPU 信息：\n{gpu_info}"
        )
        
        logger.info(f"\n\n电脑配置信息：\n{result}\n")
        return {"是否成功": True, "结果": f"电脑配置信息：\n{result}"}
    except Exception as e:
        logger.error(f"查看电脑配置信息失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------


import subprocess

@mcp.tool()
def 获取桌面完整路径() -> dict:
    """
    使用 CMD 命令获取当前用户的桌面完整路径
    并返回给你，如果用户让你在桌面创建文档，你不知道桌面完整路径，就可以使用此工具查看后再帮用户在桌面生成
    只要在桌面之类的需要知道桌面完整路径的都可以调用此工具查看！
    """
    try:
        # 使用 cmd 命令获取用户主目录，然后拼接 Desktop 路径
        user_profile = subprocess.check_output("echo %USERPROFILE%", shell=True, text=True, errors="replace").strip()
        desktop_path = f"{user_profile}\\Desktop"
        
        result = f"当前用户的桌面完整路径：{desktop_path}"
        
        logger.info(result)
        return {"是否成功": True, "结果": result}
    except Exception as e:
        logger.error(f"获取桌面路径失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------


# 工具：更换桌面壁纸
@mcp.tool()
def 更换桌面壁纸(content: str) -> dict:
    """
    根据关键词从在线壁纸 API 获取图片并设置为 Windows 桌面静态壁纸。最低1080P，最高4k
    参数:
        content (str): 壁纸类型关键词，例如 "风景"、"动漫"、"美女"、"宝马"、"斑马" 等。
                       留空，则返回随机类型壁纸。

    """
    api_root = "https://wp.upx8.com/api.php"
    save_dir = r"C:\xiaozhi\MCP\MCP_Windows\组件\MCP工具服务组件\下载\壁纸图片"
    os.makedirs(save_dir, exist_ok=True)

    # 统一主题命名：用户输入为空 → “随机”
    theme = content.strip() if content.strip() else "随机"

    try:
        # 1. 取 302 真实直链
        params = {"content": content.strip()} if content.strip() else {}
        resp = requests.get(api_root, params=params, timeout=15, allow_redirects=False)
        resp.raise_for_status()
        image_url = resp.headers.get("Location") or resp.headers.get("location")
        if not image_url:
            raise ValueError("未能获取壁纸，可尝试更换关键词！")

        # 2. 下载
        img_resp = requests.get(image_url, timeout=15, stream=True)
        img_resp.raise_for_status()

        # 3. 生成文件名：20250817-204728=风景.jpg
        file_name = f"{time.strftime('%Y%m%d-%H%M%S')}={theme}.jpg"
        local_path = os.path.join(save_dir, file_name)

        with open(local_path, "wb") as f:
            for chunk in img_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # 4. 设为桌面壁纸
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, local_path, 0x01 | 0x02)

        logger.info(f"桌面壁纸已更换，类型：{theme}")
        return {
            "是否成功": True,
            "壁纸类型": theme
        }

    except Exception as e:
        logger.error(f"更换桌面壁纸失败: {e}")
        return {"是否成功": False, "错误，可尝试更换关键词！": str(e)}
    
    
# -------------------------------------------------------------------------------------------------





#以下为PPT控制工具


# -------------------------------------------------------------------------------------------------

# PPT_上一页
@mcp.tool()
def PPT_上一页或上一步() -> dict:
    """
    模拟按下 左键 上一页或上一步 操作
    """
    try:

        # 模拟 左键 操作
        pyautogui.hotkey('left')

        logger.info(f"\n\n已尝试按下 向左键 控制上一页或上一步\n")
        return {"是否成功": True, "结果": f"已尝试按下 向左键 控制上一页或上一步"}
    except Exception as e:
        logger.error(f"\n\n错误！失败！: {str(e)}\n")
        return {"是否成功": False, "错误！失败！": str(e)}

# -------------------------------------------------------------------------------------------------


# PPT_下一页
@mcp.tool()
def PPT_下一页或下一步() -> dict:
    """
    模拟按下 右键 下一页或下一步 操作
    """
    try:
        # 模拟 右键 操作
        pyautogui.hotkey('right')
        logger.info(f"\n\n已尝试按下 向右键 控制下一页或下一步\n")
        return {"是否成功": True, "结果": f"已尝试按下 向右键 控制下一页或下一步"}
    except Exception as e:
            logger.error(f"\n\n错误！失败！: {str(e)}\n")
            return {"是否成功": False, "错误！失败！": str(e)}


# -------------------------------------------------------------------------------------------------


# PPT_结束放映
@mcp.tool()
def PPT_结束放映() -> dict:
    """
    模拟按下 Esc 键 结束放映
    """
    try:
        # 模拟 Esc 操作
        pyautogui.press('esc')
        logger.info(f"\n\n已尝试按下 Esc 键 结束放映\n")
        return {"是否成功": True, "结果": f"已尝试按下 Esc 键 结束放映"}
    except Exception as e:
            logger.error(f"\n\n错误！失败！: {str(e)}\n")
            return {"是否成功": False, "错误！失败！": str(e)}


# -------------------------------------------------------------------------------------------------

# PPT_从当页开始放映
@mcp.tool()
def PPT_从当页开始放映() -> dict:
    """
    模拟按下 Shift + F5 键 从当页开始放映
    """
    try:
        # 模拟 Shift + F5 操作
        pyautogui.hotkey('shift', 'f5')
        logger.info(f"\n\n已尝试按下 Shift + F5 键 从当页开始放映\n")
        return {"是否成功": True, "结果": f"已尝试按下 Shift + F5 键 从当页开始放映"}
    except Exception as e:
            logger.error(f"\n\n错误！失败！: {str(e)}\n")
            return {"是否成功": False, "错误！失败！": str(e)}


# -------------------------------------------------------------------------------------------------


# PPT_从头放映
@mcp.tool()
def PPT_从头放映() -> dict:
    """
    模拟按下 F5 键 从头放映
    """
    try:
        # 模拟 F5 操作
        pyautogui.press('f5')
        logger.info(f"\n\n已尝试按下 F5 键 从头放映\n")
        return {"是否成功": True, "结果": f"已尝试按下 F5 键 从头放映"}
    except Exception as e:
            logger.error(f"\n\n错误！失败！: {str(e)}\n")
            return {"是否成功": False, "错误！失败！": str(e)}


    
# 在文档上查找内容
@mcp.tool()
def 在文档上查找内容(要查找的内容: str) -> dict:
    """
    模拟按下 Ctrl + F 键   粘贴内容  Enter搜索内容
    """
    try:
        #等待
        time.sleep(0.3)
        # 模拟 ESC 操作
        pyautogui.hotkey('esc')

        # 模拟 Ctrl + F 操作
        pyautogui.hotkey('ctrl', 'f')
        #等待
        time.sleep(0.1)
        # 粘贴内容
        pyperclip.copy(要查找的内容)
        #等待
        time.sleep(0.3)
        # 模拟 Ctrl + A 操作
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        # 模拟 Ctrl + V 操作
        pyautogui.hotkey('ctrl', 'v')
        #等待
        time.sleep(0.3)
        # 模拟 Enter 操作
        pyautogui.press('enter')
        logger.info(f"\n\n已尝试按下 Ctrl + F 键   粘贴内容  Enter 搜索查找内容：{要查找的内容}\n")
        return {"是否成功": True, "结果": f"已尝试按下 Ctrl + F 键   粘贴内容  Enter 搜索查找内容"}
    except Exception as e:
            logger.error(f"\n\n错误！失败！: {str(e)}\n")
            return {"是否成功": False, "错误！失败！": str(e)}







# -------------------------------------------------------------------------------------------------



# 检查是否允许使用微信工具  使用即同意协议
允许使用微信发消息工具 = False
允许使用微信发消息工具判断文件路径 = r"C:\xiaozhi\MCP\MCP_Windows\数据\允许使用微信发消息工具.DLL"
if os.path.exists(允许使用微信发消息工具判断文件路径):
    允许使用微信发消息工具 = True

# 根据权限文件动态注册微信工具
if 允许使用微信发消息工具:
    @mcp.tool()
    def 向微信指定联系人发送内容(微信联系人: str, 要发送的内容: str) -> dict:
        """
        以打开微信的方式显示微信窗口，搜索联系人显示联系人对话框，输入内容后直接回车发送
        因为是完全自动化指令，没有任何空隙，内容发错可能会有影响
        一定要向用户确认要发送的联系人和内容！
        参数：
        微信联系人: 要搜索的微信联系人  比如 "文件传输助手"
        要发送的内容: 要发送的内容  比如 "晚上好"
        模拟操作，所以发送速度较慢请耐心等待返回
        """
        try:

            logger.info(f"\n\n开始执行向：{微信联系人}\n发送内容！\n")
            #使用快捷键 Ctrl+Alt+W 呼出微信界面
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            # 如果是预设程序名称，则获取对应的路径
            program_path = preset_programs.get("微信", "微信")
            if program_path.endswith('.lnk'):
                # 如果是.lnk文件，使用os.startfile打开
            # 运行微信以显示窗口
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
            else:
            # 运行微信以显示窗口 运行多次保证显示
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)           
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)
            # 等待
            time.sleep(0.2)
            #模拟 Ctrl+F 跳转到搜索
            pyautogui.hotkey('Ctrl', 'f')
            # 等待
            time.sleep(0.1)
            # 复制要搜索的联系人到剪贴板
            pyperclip.copy(微信联系人)
            # 等待0.1秒
            time.sleep(0.1)
            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(1.6)
            # 模拟 按下 Enter 操作 选中进入联系人对话框
            pyautogui.hotkey('Enter')
            #准备发送消息
            # 等待
            time.sleep(0.6)
            #使用快捷键 Ctrl+Alt+W 隐藏再呼出微信界面，确保光标在输入框
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            time.sleep(0.5)
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            # 复制要发送的内容到剪贴板
            pyperclip.copy(要发送的内容)
            # 等待
            time.sleep(0.5)
            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(0.2)
            # 模拟 按下 Enter 操作   发送内容
            pyautogui.hotkey('Enter')

            logger.info(f"\n\n已尝试向联系人：{微信联系人}\n发送了内容：{要发送的内容}\n")
            return {"是否成功": True, "结果": f"已尝试向联系人：{微信联系人}]\n发送了内容：{要发送的内容}"}
        except Exception as e:
            logger.error(f"\n\n错误！运行失败！: {str(e)}  可能未添加微信路径预设！\n")
            return {"是否成功": False, "错误！运行失败！ 可能未添加微信路径预设！": str(e)}

# -------------------------------------------------------------------------------------------------



    @mcp.tool()
    def 向微信联系人发送指定文件(文件路径: str, 微信联系人: str) -> dict:

        """
        向微信指定联系人发送指定文件
        参数：
            文件路径：（要发送的文件完整路径）如：C:\Windows\explorer.exe
            微信联系人：（文件发送的目标联系人）
        """
        try:

            logger.info(f"\n\n开始执行向：{微信联系人}\n发送文件！\n")
            #使用快捷键 Ctrl+Alt+W 呼出微信界面
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            # 如果是预设程序名称，则获取对应的路径
            program_path = preset_programs.get("微信", "微信")
            if program_path.endswith('.lnk'):
                # 如果是.lnk文件，使用os.startfile打开
            # 运行微信以显示窗口
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
            else:
            # 运行微信以显示窗口 运行多次保证显示
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)           
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)
            # 等待
            time.sleep(0.2)
            #模拟 Ctrl+F 跳转到搜索
            pyautogui.hotkey('Ctrl', 'f')
            # 等待
            time.sleep(0.1)
            # 复制要搜索的联系人到剪贴板
            pyperclip.copy(微信联系人)
            # 等待0.1秒
            time.sleep(0.1)
            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(1.6)
            # 模拟 按下 Enter 操作 选中进入联系人对话框
            pyautogui.hotkey('Enter')
            #准备发送文件

            abspath = os.path.abspath(文件路径)
            # 启动 explorer，但不捕获输出
            subprocess.Popen(['explorer', '/select,', abspath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            folder_name = os.path.basename(os.path.dirname(abspath))
            ps = f'''
            $wshell = New-Object -ComObject WScript.Shell
            while (-not (Get-Process explorer | Where-Object {{$_.MainWindowTitle -like "*{folder_name}*"}})) {{Start-Sleep -Milliseconds 200}}
            [void]$wshell.AppActivate((Get-Process explorer | Where-Object {{$_.MainWindowTitle -like "*{folder_name}*"}}).MainWindowTitle)
            '''
            subprocess.Popen(['powershell', '-NoProfile', '-Command', ps], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            time.sleep(3.6)

            pyautogui.hotkey('ctrl', 'c')
            # 等待
            time.sleep(0.5)
            pyautogui.hotkey('alt', 'f4')

            # 等待
            time.sleep(1.5)

            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(1)
            # 模拟 按下 Enter 操作   发送内容
            pyautogui.hotkey('Enter')


            logger.info(f"\n\n已尝试向：{微信联系人}\n发送了文件：{文件路径} ！\n")
            return {"是否成功": True, "结果": f"已尝试向联系人：{微信联系人}\n发送了文件：{文件路径}"}
        except Exception as e:
            logger.error(f"\n\n错误！运行失败！: {str(e)}  可能未添加微信路径预设！\n")
            return {"是否成功": False, "错误！运行失败！ 可能未添加微信路径预设！": str(e)}


# -------------------------------------------------------------------------------------------------




    @mcp.tool()
    def 向微信指定联系人发送复制的内容(微信联系人: str) -> dict:

        """
        向微信指定联系人发送刚刚复制的内容。比如说刚刚的截图
        以打开微信的方式显示微信窗口，搜索联系人显示联系人对话框，输入内容后直接回车发送
        因为是完全自动化指令，没有任何空隙，内容发错可能会有影响
        一定要向用户确认要发送的联系人和内容！
        参数：
        微信联系人: 要搜索的微信联系人  比如 "张三"
        模拟操作，所以发送速度较慢请耐心等待返回
        """
        try:

            logger.info(f"\n\n开始执行向：{微信联系人}\n发送复制的内容！\n")
            #使用快捷键 Ctrl+Alt+W 呼出微信界面
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            # 如果是预设程序名称，则获取对应的路径
            program_path = preset_programs.get("微信", "微信")
            if program_path.endswith('.lnk'):
                # 如果是.lnk文件，使用os.startfile打开
            # 运行微信以显示窗口
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
                os.startfile(program_path)
                # 等待
                time.sleep(0.1)
            else:
            # 运行微信以显示窗口 运行多次保证显示
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)           
                subprocess.Popen(program_path)
                # 等待
                time.sleep(0.1)
            # 等待
            time.sleep(0.2)
            #模拟 Ctrl+F 跳转到搜索
            pyautogui.hotkey('Ctrl', 'f')
            # 等待
            time.sleep(0.1)
            # 复制要搜索的联系人到剪贴板
            pyperclip.copy(微信联系人)
            # 等待0.1秒
            time.sleep(0.1)
            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(1)
            # 模拟 按下 Enter 操作 选中进入联系人对话框
            pyautogui.hotkey('Enter')
            #准备发送消息
            # 等待
            time.sleep(0.6)
            #使用快捷键 Ctrl+Alt+W 隐藏再呼出微信界面，确保光标在输入框
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            time.sleep(0.5)
            pyautogui.hotkey('Ctrl', 'alt', 'w')
            # 等待
            time.sleep(0.5)
            # 模拟 Ctrl+V 操作 粘贴要搜索的联系人
            pyautogui.hotkey('Ctrl', 'v')
            # 等待
            time.sleep(0.2)
            # 模拟 按下 Enter 操作   发送内容
            pyautogui.hotkey('Enter')

            logger.info(f"\n\n已尝试向联系人：{微信联系人}\n发送了复制的内容！\n")
            return {"是否成功": True, "结果": f"已尝试向联系人：{微信联系人}\n发送了复制的内容！"}
        except Exception as e:
            logger.error(f"\n\n错误！运行失败！: {str(e)}  可能未添加微信路径预设！\n")
            return {"是否成功": False, "错误！运行失败！ 可能未添加微信路径预设！": str(e)}

# -------------------------------------------------------------------------------------------------




#以下为Al_API工具函数




# -------------------------------------------------------------------------------------------------



# 新增工具函数：获取心灵毒鸡汤
@mcp.tool()
def 获取心灵毒鸡汤() -> dict:
    """
    获取心灵毒鸡汤
    帮用户说：“来碗鸡汤”/“来碗心灵毒鸡汤” 调用此工具获取，不要自己编
    """
    try:
        url = "https://v3.alapi.cn/api/soul"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                logger.info(f"\n\n获取心灵毒鸡汤成功：{data.get('data', {}).get('content', '获取失败')}\n")
                return {"是否成功": True, "结果": data.get('data', {}).get('content', '获取失败')}
            else:
                logger.error(f"获取心灵毒鸡汤失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------


# 新增工具函数：获取早报
@mcp.tool()
def 获取早报() -> dict:
    """
    获取早报
    """
    try:
        url = "https://v3.alapi.cn/api/zaobao"
        querystring = {"token": token, "format": "json"}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                news_list = data.get("data", {}).get("news", [])
                formatted_news = "\n".join([f"{index + 1}. {news}" for index, news in enumerate(news_list)])
                weiyu = data.get("data", {}).get("weiyu", "无微语")
                logger.info(f"\n\n获取早报成功：\n{formatted_news}\n微语：{weiyu}\n")
                return {"是否成功": True, "结果": {"早报": formatted_news, "微语": weiyu}}
            else:
                logger.error(f"获取早报失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------


# 新增工具函数：获取舔狗日记
@mcp.tool()
def 获取舔狗日记() -> dict:
    """
    获取舔狗日记
    """
    try:
        url = "https://v3.alapi.cn/api/dog"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                logger.info(f"\n\n获取舔狗日记成功：{data.get('data', {}).get('content', '获取失败')}\n")
                return {"是否成功": True, "结果": data.get('data', {}).get('content', '获取失败')}
            else:
                logger.error(f"获取舔狗日记失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------
# 新增工具函数：获取一言
@mcp.tool()
def 获取一言() -> dict:
    """
    获取一言
    """
    try:
        url = "https://v3.alapi.cn/api/hitokoto"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                hitokoto = data.get('data', {}).get('hitokoto', '获取失败')
                from_ = data.get('data', {}).get('from', '未知来源')
                creator = data.get('data', {}).get('creator', '未知作者')
                logger.info(f"\n\n获取一言成功：{hitokoto}\n")
                return {"是否成功": True, "结果": {"一言": hitokoto, "来源": from_, "作者": creator}}
            else:
                logger.error(f"获取一言失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------
# 新增工具函数：获取土味情话
@mcp.tool()
def 获取土味情话() -> dict:
    """
    获取土味情话
    """
    try:
        url = "https://v3.alapi.cn/api/qinghua"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                logger.info(f"\n\n获取土味情话成功：{data.get('data', {}).get('content', '获取失败')}\n")
                return {"是否成功": True, "结果": data.get('data', {}).get('content', '获取失败')}
            else:
                logger.error(f"获取土味情话失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------
# 新增工具函数：获取笑话大全
@mcp.tool()
def 获取笑话大全() -> dict:
    """
    获取笑话大全
    调用过一次会返回10条,因为API接口受限,不用调用多次!!!
    """
    try:
        url = "https://v3.alapi.cn/api/joke"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                jokes = data.get('data', [])
                formatted_jokes = "\n\n".join([f"{index + 1}. {joke.get('content', '获取失败')}" for index, joke in enumerate(jokes)])
                logger.info(f"\n\n获取笑话大全成功：\n{formatted_jokes}\n")
                return {"是否成功": True, "结果": formatted_jokes}
            else:
                logger.error(f"获取笑话大全失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------
# 新增工具函数：获取油价查询
@mcp.tool()
def 查询油价() -> dict:
    """
    获取油价查询
    """
    try:
        url = "https://v3.alapi.cn/api/oil"
        querystring = {"token": token}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                formatted_oil_prices = ""
                for item in data.get('data', []):
                    formatted_oil_prices += f"省份：{item.get('province', '未知省份')}\n"
                    formatted_oil_prices += f"    89号汽油：{item.get('o89', '无数据')} 元/升\n"
                    formatted_oil_prices += f"    92号汽油：{item.get('o92', '无数据')} 元/升\n"
                    formatted_oil_prices += f"    95号汽油：{item.get('o95', '无数据')} 元/升\n"
                    formatted_oil_prices += f"    98号汽油：{item.get('o98', '无数据')} 元/升\n"
                    formatted_oil_prices += f"    0号柴油：{item.get('o0', '无数据')} 元/升\n"
                    formatted_oil_prices += "-" * 50 + "\n"
                logger.info(f"\n\n获取油价查询成功：\n{formatted_oil_prices}\n")
                return {"是否成功": True, "result": formatted_oil_prices}
            else:
                logger.error(f"获取油价查询失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}

# -------------------------------------------------------------------------------------------------


# 新增工具函数：查询快递V2
@mcp.tool()
def 查询快递V2(tracking_number: str, company: str = "auto") -> dict:
    """
    获取快递查询V2 （计次接口）
    参数： tracking_number: 快递单号
    参数： company: 快递公司，默认为自动识别
    """
    try:
        url = "https://v3.alapi.cn/api/tracking"
        querystring = {"token": token, "number": tracking_number, "com": company}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                formatted_tracking = f"快递单号：{data.get('data', {}).get('number', '未知单号')}\n"
                formatted_tracking += f"快递公司：{data.get('data', {}).get('exp_name', '未知公司')}\n"
                formatted_tracking += f"状态：{data.get('data', {}).get('status_text', '未知状态')}\n"
                formatted_tracking += "物流信息：\n"
                for item in data.get('data', {}).get('info', []):
                    formatted_tracking += f"时间：{item.get('time', '未知时间')} - {item.get('content', '未知内容')}\n"
                logger.info(f"\n\n获取快递查询成功：\n{formatted_tracking}\n")
                return {"是否成功": True, "result": formatted_tracking}
            else:
                logger.error(f"获取快递查询失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}


# -------------------------------------------------------------------------------------------------

# 新增工具函数：查询快递V1
@mcp.tool()
def 查询快递V1(tracking_number: str, phone: str = "") -> dict:
    """
    快速查询快递V1 （会员接口）
    参数： tracking_number: 快递单号
    参数： phone: 寄/收件人手机号后四位，顺丰快递和中通快递必填
    """
    try:
        url = "https://v3.alapi.cn/api/kd"
        querystring = {"token": token, "number": tracking_number, "com": "", "phone": phone}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                formatted_tracking = f"快递单号：{data.get('data', {}).get('number', '未知单号')}\n"
                formatted_tracking += f"快递公司：{data.get('data', {}).get('exp_name', '未知公司')}\n"
                formatted_tracking += f"状态：{data.get('data', {}).get('status_text', '未知状态')}\n"
                formatted_tracking += "物流信息：\n"
                for item in data.get('data', {}).get('info', []):
                    formatted_tracking += f"时间：{item.get('time', '未知时间')} - {item.get('content', '未知内容')}\n"
                logger.info(f"\n\n快速获取快递查询成功：\n{formatted_tracking}\n")
                return {"是否成功": True, "result": formatted_tracking}
            else:
                logger.error(f"快速获取快递查询失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"快速查询请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"快速查询请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"快速查询请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"快速查询请求网页时发生错误：{e}"}


# -------------------------------------------------------------------------------------------------


# 新增工具函数：获取星座运势
@mcp.tool()
def 获取星座运势(constellation: str) -> dict:
    """
    获取星座运势
    参数： constellation: 星座名称，支持：aries 白羊座, taurus 金牛座, gemini 双子座, cancer 巨蟹座, leo 狮子座, virgo 处女座, libra 天秤座, scorpio 天蝎座, sagittarius 射手座, capricorn 摩羯座, aquarius 水瓶座, pisces 双鱼座
    
    回复用户完整的运势解读！！！
    
    """
    try:
        url = "https://v3.alapi.cn/api/star"
        payload = {
            "token": token,
            "star": constellation
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
    #        logger.info(f"获取星座运势返回的内容：{data}")     #原始数据
            if data.get("success", False):
                day_data = data.get('data', {})
                formatted_horoscope = f"日期：{day_data.get('day', {}).get('date', '未知日期')}\n"
                formatted_horoscope += f"星座：{constellation}\n"
                formatted_horoscope += f"综合运势：{day_data.get('day', {}).get('all', '未知')} - {day_data.get('day', {}).get('all_text', '未知')}\n"
                formatted_horoscope += f"爱情运势：{day_data.get('day', {}).get('love', '未知')} - {day_data.get('day', {}).get('love_text', '未知')}\n"
                formatted_horoscope += f"工作运势：{day_data.get('day', {}).get('work', '未知')} - {day_data.get('day', {}).get('work_text', '未知')}\n"
                formatted_horoscope += f"财运：{day_data.get('day', {}).get('money', '未知')} - {day_data.get('day', {}).get('money_text', '未知')}\n"
                formatted_horoscope += f"健康运势：{day_data.get('day', {}).get('health', '未知')} - {day_data.get('day', {}).get('health_text', '未知')}\n"
                formatted_horoscope += f"幸运颜色：{day_data.get('day', {}).get('lucky_color', '未知')}\n"
                formatted_horoscope += f"幸运数字：{day_data.get('day', {}).get('lucky_number', '未知')}\n"
                # 记录格式化后的星座运势信息
                logger.info(f"\n\n星座运势：\n{formatted_horoscope}")
                return {"是否成功": True, "result": formatted_horoscope}
            else:
                logger.error(f"获取星座运势失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}
    

# -------------------------------------------------------------------------------------------------


# 新增工具函数：获取节假日查询
# 新增工具函数：获取节假日查询
@mcp.tool()
def 查询节假日(year: str = None) -> dict:
    """
    获取节假日查询，可指定年份
    参数： year: 可选参数，指定查询的年份，默认为当前年份,不能大于当前年
    """
    try:
        # 如果未指定年份，则使用当前年份
        if year is None:
            year = str(datetime.datetime.now().year)
        
        url = "https://v3.alapi.cn/api/holiday"
        querystring = {"token": token, "year": year}
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, params=querystring, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                formatted_holidays = f"{'*' * 50}\n{year}年节假日信息\n{'*' * 50}\n"
                for item in data.get('data', []):
                    # 格式化日期显示，例如 2025-01-01 显示为 1月1日
                    date_parts = item.get('date', '未知日期').split('-')
                    if len(date_parts) >= 3:
                        formatted_date = f"{date_parts[1]}月{date_parts[2]}日"
                    else:
                        formatted_date = item.get('date', '未知日期')
                    
                    formatted_holidays += f"节日名称：{item.get('name', '未知节日')}\n"
                    formatted_holidays += f"日期：{formatted_date}\n"
                    formatted_holidays += f"放假或加班：{'休' if item.get('is_off_day', 0) == 1 else '班'}\n"
                    formatted_holidays += "-" * 50 + "\n"
                
                logger.info(f"\n\n获取节假日查询成功：\n{formatted_holidays}\n")
                return {"是否成功": True, "result": formatted_holidays}
            else:
                logger.error(f"获取节假日查询失败：{data.get('message', '未知错误')}")
                return {"是否成功": False, "错误": data.get('message', '未知错误')}
        else:
            logger.error(f"请求失败，状态码：{response.status_code}")
            return {"是否成功": False, "错误": f"请求失败，状态码：{response.status_code}"}
    except requests.RequestException as e:
        logger.error(f"请求网页时发生错误：{e}")
        return {"是否成功": False, "错误": f"请求网页时发生错误：{e}"}
    except Exception as e:
        logger.error(f"查询节假日时发生错误：{e}")
        return {"是否成功": False, "错误": f"查询节假日时发生错误：{e}"}
# -------------------------------------------------------------------------------------------------


@mcp.tool()
def 设置主人电脑系统深浅色主题(params: dict) -> dict:
    """
    设置 Windows 系统的浅色/深色主题
    调用方法：设置主人电脑系统深浅色主题({"深色": false})  # true = 深色，false = 浅色
    """
    import winreg
    try:
        dark = bool(params.get("深色", True))
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value = 0 if dark else 1

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            # 两个关键值都改！
            winreg.SetValueEx(key, "AppsUseLightTheme",    0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "ColorPrevalence",      0, winreg.REG_DWORD, 1)

        logger.info(f"\n\n已切换为 {'深色' if dark else '浅色'} 主题\n")
        return {"是否成功": True, "结果": f"已切换为 {'深色' if dark else '浅色'} 主题"}
    except Exception as e:
        logger.error(f"切换主题失败: {str(e)}")
        return {"是否成功": False, "错误": str(e)}

# -------------------------------------------------------------------------------------------------



#以下为洛雪音乐软件控制工具


# -------------------------------------------------------------------------------------------------


# 需要设置软件内全局快捷键

# 显示/隐藏程序  Alt+L

# 播放/暂停控制  Ctrl+Shift+空格

# 上一曲控制     Ctrl+Shift+A

# 下一曲控制     Ctrl+Shift+DD


# 需设置软件内快捷方式

#  聚焦搜索框    F1




# 定义工具函数：作者环境下可用的专属工具

# 检查是否是作者工作环境
使用控制洛雪音乐工具 = False
使用控制洛雪音乐工具判断文件路径 = r"C:\xiaozhi\MCP\MCP_Windows\数据\使用控制洛雪音乐工具.DLL"
if os.path.exists(使用控制洛雪音乐工具判断文件路径):
    使用控制洛雪音乐工具 = True

    # 根据权限文件动态注册工具
    if 使用控制洛雪音乐工具:


        @mcp.tool()
        def 洛雪音乐_搜索并播放音乐(要搜索的歌曲: str) -> dict:
            """
            以打开洛雪音乐的方式显示音乐窗口
            因为是完全自动化指令，没有任何空隙，内容发错可能会有影响
            可以向用户确认要搜索的歌曲！
            参数：
            要搜索的歌曲: 要搜索的歌曲  比如 "茫"
            模拟操作，所以操作速度较慢请耐心等待返回
            """
            try:

                logger.info(f"\n\n开始执行搜索并播放音乐：{要搜索的歌曲}！\n")
                #使用快捷键 'Alt', 'l' 呼出洛雪音乐界面
                pyautogui.hotkey('Alt', 'l')
                # 如果是预设程序名称，则获取对应的路径
                program_path = preset_programs.get("洛雪音乐", "洛雪音乐")
                if program_path.endswith('.lnk'):
                    # 如果是.lnk文件，使用os.startfile打开
                # 运行以显示窗口
                    os.startfile(program_path)
                    # 等待
                    time.sleep(0.1)
                    os.startfile(program_path)
                    # 等待
                    time.sleep(0.1)
                else:
                # 运行以显示窗口 运行多次保证显示
                    subprocess.Popen(program_path)
                    # 等待
                    time.sleep(0.1)           
                    subprocess.Popen(program_path)
                    # 等待
                    time.sleep(0.1)
                #准备搜索歌曲
                # 等待
                time.sleep(1)
                #模拟按下F1聚焦搜索框
                pyautogui.hotkey('F1')
                # 复制要搜索的歌曲名到剪贴板
                pyperclip.copy(要搜索的歌曲)
                # 模拟 Ctrl+A 操作 选中搜索框的内容覆盖
                pyautogui.hotkey('Ctrl', 'a')
                # 模拟 Ctrl+V 操作 粘贴要搜索的歌曲名
                pyautogui.hotkey('Ctrl', 'v')
                # 等待
                time.sleep(0)
                # 模拟 按下 Enter 操作 选中进入联系人对话框
                pyautogui.hotkey('Enter')
                # 等待
                time.sleep(1.6)
                #连按5次Tab 将光标移动到搜索到的第1首
                # 模拟 Tab 6次 间隔0.1秒
                for _ in range(6):
                    pyautogui.hotkey('Tab')
                    # 等待0.1秒
                    time.sleep(0.1)
                # 等待
                time.sleep(0.5)

                # 模拟 按下 Enter 操作 播放第1首搜索到的歌
                pyautogui.hotkey('Enter')

                logger.info(f"\n\n已尝试洛雪音乐搜索并播放歌曲：{要搜索的歌曲}\n")
                return {"是否成功": True, "结果": f"n已尝试洛雪音乐搜索并播放歌曲：{要搜索的歌曲}"}
            except Exception as e:
                logger.error(f"\n\n错误！洛雪音乐运行失败！: {str(e)}\n")
                return {"是否成功": False, "错误！洛雪音乐运行失败！": str(e)}

        # -------------------------------------------------------------------------------------------------


        @mcp.tool()
        def 洛雪音乐_暂停或继续播放音乐() -> dict:
            """
            模拟按下Ctrl+Shift+空格 暂停或继续播放音乐
            """
            try:

                # 模拟 Ctrl+Shift+空格 操作 控制全局暂停或播放音乐
                pyautogui.hotkey('Ctrl', 'Shift', 'Space')

                logger.info(f"\n\n已尝试按下洛雪音乐暂停或播放快捷键\n")
                return {"是否成功": True, "结果": f"已尝试按下洛雪音乐暂停或播放快捷键"}
            except Exception as e:
                logger.error(f"\n\n错误！洛雪音乐运行失败！: {str(e)}\n")
                return {"是否成功": False, "错误！洛雪音乐运行失败！": str(e)}

        # -------------------------------------------------------------------------------------------------

        

        @mcp.tool()
        def 洛雪音乐_上一首音乐() -> dict:
            """
            模拟按下全局快捷键Ctrl+Shift+A 播放上一首音乐
            """
            try:

                # 模拟 按下 Ctrl+Shift+A 操作 跳转到上一首歌
                
                pyautogui.hotkey('Ctrl', 'Shift', 'A')

                logger.info(f"\n\n已尝试播放洛雪音乐上一曲\n")
                return {"是否成功": True, "结果": f"已尝试播放洛雪音乐上一曲"}
            except Exception as e:
                logger.error(f"\n\n错误！洛雪音乐运行失败！: {str(e)}\n")
                return {"是否成功": False, "错误！洛雪音乐运行失败！": str(e)}

        # -------------------------------------------------------------------------------------------------


        @mcp.tool()
        def 洛雪音乐_下一首音乐() -> dict:
            """
            模拟按下全局快捷键Ctrl+Shift+D 播放下一首音乐
            """
            try:
                # 模拟 按下 Ctrl+Shift+D 操作 跳转到下一首歌
                pyautogui.hotkey('Ctrl', 'Shift', 'D')
                
                logger.info(f"\n\n已尝试播放洛雪音乐下一曲\n")
                return {"是否成功": True, "结果": f"已尝试播放洛雪音乐下一曲"}
            except Exception as e:
                    logger.error(f"\n\n错误！洛雪音乐运行失败！: {str(e)}\n")
                    return {"是否成功": False, "错误！洛雪音乐运行失败！": str(e)}


# 定义工具函数：作者环境下可用的专属工具

# 检查是否是作者工作环境
是作者工作环境 = False
是作者工作环境判断文件路径 = r"C:\粽子同学的PC.exe"
if os.path.exists(是作者工作环境判断文件路径):
    是作者工作环境 = True

    # 根据权限文件动态注册工具
    if 是作者工作环境:
        @mcp.tool()
        def 洛雪音乐_播放收藏列表() -> dict:
            """
            以打开洛雪音乐的方式显示音乐窗口
            跳转到收藏列表，自动开始播放收藏列表的歌
            模拟操作，所以操作速度较慢请耐心等待返回
            """
            try:

                logger.info(f"\n\n开始播放收藏列表！\n")
                #使用快捷键 'Alt', 'l' 呼出洛雪音乐界面
                pyautogui.hotkey('Alt', 'l')
                # 如果是预设程序名称，则获取对应的路径
                program_path = preset_programs.get("洛雪音乐", "洛雪音乐")
                if program_path.endswith('.lnk'):
                    # 如果是.lnk文件，使用os.startfile打开
                # 运行以显示窗口
                    os.startfile(program_path)
                    # 等待
                    time.sleep(0.1)
                    os.startfile(program_path)
                    # 等待
                    time.sleep(0.1)
                else:
                # 运行以显示窗口 运行多次保证显示
                    subprocess.Popen(program_path)
                    # 等待
                    time.sleep(0.1)           
                    subprocess.Popen(program_path)
                    # 等待
                    time.sleep(0.1)
                #准备搜索歌曲
                # 等待
                time.sleep(1)
                #模拟按下F1聚焦搜索框
                pyautogui.hotkey('F1')
                time.sleep(0.6)

                #连按5次 Shift + Tab 将光标移动到收藏列表

                # 模拟 Tab 3次 间隔0.1秒 
                for _ in range(3):
                    pyautogui.hotkey('Shift', 'Tab')
                    # 等待0.1秒
                    time.sleep(0.1)

                # 模拟 按下Enter进入收藏列表
                pyautogui.hotkey('Enter')
                time.sleep(0.1)

                #连按5次 Tab 将光标移动到收藏列表第1首
                # 模拟 Tab 12次 间隔0.1秒
                for _ in range(12):
                    pyautogui.hotkey('Tab')
                    # 等待0.1秒
                    time.sleep(0.1)

                # 模拟 按下 Enter 操作 播放收藏列表第1首搜歌
                pyautogui.hotkey('Enter')

                logger.info(f"\n\n已尝试播放洛雪音乐收藏列表的歌!\n")
                return {"是否成功": True, "结果": f"n已尝试播放洛雪音乐收藏列表的歌"}
            except Exception as e:
                logger.error(f"\n\n错误！洛雪音乐运行失败！: {str(e)}\n")
                return {"是否成功": False, "错误！洛雪音乐运行失败！": str(e)}

        # -------------------------------------------------------------------------------------------------




# -------------------------------------------------------------------------------------------------


#添加自己更多的API工具 或者MCP工具


# -------------------------------------------------------------------------------------------------


# 控制电脑相关功能列表（第一部分）
控制电脑功能 = [
    "1.运行电脑端程序 预设软件 或 具体路径",
    "2.在电脑上打开URL网址 网页名 或 具体URL网址",
    "3.在电脑上运行CMD指令 预设指令 或 具体指令",
    "4.官方的计算器示例",
    "5.创建文件写入内容",
    "6.读取复制内容",
    "7.填入一段内容",
    "8.回车发送",
    "9.撤销操作",
    "10.锁定电脑",
    "11.电脑关机计划",
    "12.设置电脑音量",
    "13.调用系统截图工具",
    "14.显示桌面",
    "15.查看系统资源使用情况",
    "16.查看电脑配置信息 & 获取桌面完整路径",
    "17.设置Windows系统深浅色主题",
    "18.更换桌面壁纸",
    "19.PPT_上一页或上一步",
    "20.PPT_下一页或下一步",
    "21.PPT_结束放映",
    "22.PPT_从当页开始放映",
    "23.PPT_从头放映",
    "24.在文档上查找内容"
]

# AI 平台相关的 API 能力列表（第二部分）
API功能 = [
    "\n支持的 AI 平台 API 能力：\n",
    "1.获取心灵毒鸡汤",
    "2.获取早报",
    "3.获取舔狗日记",
    "4.获取一言",
    "5.获取土味情话",
    "6.获取笑话大全",
    "7.获取油价查询",
    "8.查询快递 V1",
    "9.查询快递 V2",
    "10.获取星座运势",
    "11.获取节假日查询"
]

# 动态插入工具功能到第一部分
if 允许使用微信发消息工具:
    控制电脑功能.append("25.向微信指定联系人发送内容")
    控制电脑功能.append("26.向微信联系人发送指定文件")
    控制电脑功能.append("27.向微信指定联系人发送复制的内容")

# 动态插入工具功能
if 使用控制洛雪音乐工具:

    洛雪音乐控制 = [
        "\n支持的 洛雪音乐控制工具：\n",
        "1.洛雪音乐_搜索并播放音",
        "2.洛雪音乐_暂停或继续播放音乐",  
        "3.洛雪音乐_下一首音乐",
        "4.洛雪音乐_上一首音乐",
    ]

    # 动态插入工具功能
    if 是作者工作环境:
        
        洛雪音乐控制.append("5.洛雪音乐_播放收藏列表")


# 动态插入工具功能
if 使用控制洛雪音乐工具:

    # 将两部分功能列表合并
    功能内容 = 控制电脑功能 + API功能 + 洛雪音乐控制

else:
    功能内容 = 控制电脑功能 + API功能
    


# -------------------------------------------------------------------------------------------------

# 主程序入口
if __name__ == "__main__":
    logger.info("\n\n\tMCP_Windows服务已启动！等待调用！\n\n当前支持：\n" + "\n".join(功能内容) + "\n\n快尝试让小智的能力吧！\n")
    logger.info("\n\n\t\b版本：v42.28.26 (2025-10-18 更新)\n\t\tBy[粽子同学]\n\n")
    mcp.run(transport="stdio")
# -------------------------------------------------------------------------------------------------

