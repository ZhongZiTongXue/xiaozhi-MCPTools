import os
import shutil
import psutil
from pathlib import Path

# 路径配置
base_dir = Path(r"C:\xiaozhi\MCP\MCP_Windows\组件\存储占用感知服务\数据")
log_files = {
    "disk_total": base_dir / "磁盘总空间.txt",
    "disk_free": base_dir / "磁盘剩余可用空间.txt",
    "folder_size": base_dir / "软件占用空间.txt",
    "success_flag": base_dir / "读取完成.EXE"
}

# 目标文件夹
target_folder = Path(r"C:\xiaozhi")

# 创建目标目录（如果不存在）
base_dir.mkdir(parents=True, exist_ok=True)

def get_disk_usage_gb(drive):
    """获取磁盘总空间和剩余空间（单位：GB，保留两位小数）"""
    usage = psutil.disk_usage(drive)
    total_gb = round(usage.total / (1024**3), 2)
    free_gb = round(usage.free / (1024**3), 2)
    return total_gb, free_gb

def get_folder_size_mb(folder):
    """获取文件夹总大小（单位：MB，保留两位小数）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except (OSError, FileNotFoundError):
                continue  # 跳过无法访问的文件
    return round(total_size / (1024**2), 2)

def write_and_log(file_path, content):
    """写入文件并打印日志"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(content))
    print(f"[日志] 写入文件：{file_path} 内容：{content}")

def main():
    print("=== 磁盘空间与文件夹占用统计 ===")

    # 获取磁盘空间（以 C 盘为例）
    drive = "C:\\"
    total_gb, free_gb = get_disk_usage_gb(drive)
    write_and_log(log_files["disk_total"], total_gb)
    write_and_log(log_files["disk_free"], free_gb)

    # 获取文件夹大小
    if target_folder.exists():
        folder_size_mb = get_folder_size_mb(target_folder)
        write_and_log(log_files["folder_size"], folder_size_mb)
    else:
        print(f"[警告] 文件夹不存在：{target_folder}")

    # 写入读取成功标志
    success_msg = "读取成功，数据已更新"
    write_and_log(log_files["success_flag"], success_msg)

    print("=== 完成 ===")

if __name__ == "__main__":
    main()