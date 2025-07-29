import requests
import os
import sys
import re
import time
import argparse

# 文件路径
ota_link_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\OTA链接.exe"
download_dir = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务"
downloaded_file_path = os.path.join(download_dir, "小智Ai-MCP链接工具_新版本安装包.exe")
text_file_path = os.path.join(download_dir, "新版本下载完成！.exe")

# 创建命令行参数解析器
parser = argparse.ArgumentParser(description="下载文件并显示进度")
parser.add_argument("--speed-limit", type=float, default=0, help="设置下载速度限制（单位：MB/s）")
args = parser.parse_args()

# 全局变量
speed_limit = args.speed_limit * 1024 * 1024  # 将MB/s转换为字节/秒

# 检查文件是否存在
if not os.path.exists(ota_link_file):
    print(f"文件不存在：{ota_link_file}")
    sys.exit()

# 从文件中读取下载链接
with open(ota_link_file, 'r') as file:
    content = file.read()

# 使用正则表达式提取 URL
match = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
if match:
    url = match.group(0)
else:
    print("未找到有效的下载链接！")
    sys.exit()

# 创建下载目录（如果不存在）
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

def download_with_progress(url, destination, speed_limit=0):
    try:
        # 获取重定向后的最终URL
        head_response = requests.head(url, allow_redirects=True)
        head_response.raise_for_status()
        
        # 获取文件大小（如果可用）
        total_size = int(head_response.headers.get('content-length', 0)) if 'content-length' in head_response.headers else None
        
        # 实际下载文件
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        
        downloaded_size = 0
        start_time = time.time()
        last_update_time = start_time
        
        # 用于计算平均速度的窗口
        speed_window = []
        window_size = 10  # 窗口大小（样本数）
        
        # 下载文件并显示进度
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    # 写入文件
                    file.write(chunk)
                    
                    # 更新下载大小
                    chunk_size = len(chunk)
                    downloaded_size += chunk_size
                    
                    # 计算经过的时间
                    current_time = time.time()
                    elapsed_time = current_time - last_update_time
                    
                    # 计算当前速度并更新窗口
                    if elapsed_time > 0:
                        current_speed = chunk_size / elapsed_time
                        if len(speed_window) >= window_size:
                            speed_window.pop(0)
                        speed_window.append(current_speed)
                        last_update_time = current_time
                    
                    # 计算平均速度
                    if speed_window:
                        avg_speed = sum(speed_window) / len(speed_window)
                    else:
                        avg_speed = 0
                    
                    # 应用速度限制
                    if speed_limit > 0 and avg_speed > 0:
                        target_time = chunk_size / speed_limit
                        actual_time = current_time - start_time
                        if actual_time < target_time:
                            time.sleep(target_time - actual_time)
                            start_time = time.time()
                    
                    # 如果有文件大小信息，显示下载进度
                    if total_size:
                        progress_percentage = (downloaded_size / total_size) * 100
                        total_mb = total_size / (1024 * 1024)
                        downloaded_mb = downloaded_size / (1024 * 1024)
                        avg_speed_mb = avg_speed / (1024 * 1024) if avg_speed > 0 else 0
                        elapsed_total = current_time - start_time
                        remaining_time = (total_size - downloaded_size) / (avg_speed if avg_speed > 0 else 1)
                        
                        # 显示下载进度，固定显示宽度
                        sys.stdout.write(f"\r下载进度: {progress_percentage:6.2f}% | 已下载: {downloaded_mb:8.2f}MB/{total_mb:8.2f}MB | 速度: {avg_speed_mb:6.2f}MB/s | 已用时间: {elapsed_total:6.2f}s | 预计剩余时间: {remaining_time:6.2f}s")
                        sys.stdout.flush()
                    else:
                        # 如果没有文件大小信息，只显示已下载大小
                        downloaded_mb = downloaded_size / (1024 * 1024)
                        avg_speed_mb = avg_speed / (1024 * 1024) if avg_speed > 0 else 0
                        elapsed_total = current_time - start_time
                        
                        # 显示下载进度，固定显示宽度
                        sys.stdout.write(f"\r已下载: {downloaded_mb:8.2f}MB | 速度: {avg_speed_mb:6.2f}MB/s | 已用时间: {elapsed_total:6.2f}s")
                        sys.stdout.flush()
        
        print("\n下载完成！")
        
        # 等待三秒再生成完成文件
        print("准备生成完成文件...")
        time.sleep(3)
        
        # 生成文本文件
        with open(text_file_path, 'w') as text_file:
            text_file.write("新版本下载完成！")
#        print(f"文本文件生成完成，保存路径：{text_file_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"\n下载失败：{e}")
    except Exception as e:
        print(f"\n发生错误：{e}")

# 调用下载函数
print("开始下载...")
download_with_progress(url, downloaded_file_path, speed_limit)