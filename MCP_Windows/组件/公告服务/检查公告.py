

import paho.mqtt.client as mqtt
import time
import os
import threading
import sys  # 导入 sys 模块

HOST = "bemfa.com"
PORT = 9501
client_id = "ac9a9f2b686bb4257867806c1dcfaf67"  
topic = "MCPToolsVersion004"  # 定义主题

message = "请求公告"

timeout = 10  # 超时时间（秒）
timeout_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\公告服务\状态\响应超时.exe"
new_version_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\公告服务\状态\有新公告.exe"
up_to_date_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\公告服务\状态\未有新公告.exe"

# 从文本文档中读取公告标识号
current_version_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\公告服务\公告标识号.txt"

# 读取当前公告标识号
def read_current_version():
    if os.path.exists(current_version_file):
        with open(current_version_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return content
    print(f"无法读取公告标识号文件：{current_version_file}，使用默认值 10")
    return "10"

# 当前公告标识号
current_version = read_current_version()

# 删除已存在的文件
def delete_files():
    if os.path.exists(timeout_file):
        os.remove(timeout_file)
    if os.path.exists(new_version_file):
        os.remove(new_version_file)
    if os.path.exists(up_to_date_file):
        os.remove(up_to_date_file)

# 连接并订阅
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)  # 订阅消息

# 订阅成功
def on_subscribe(client, userdata, mid, granted_qos):
    global timer
    print("订阅成功= %d" % granted_qos)
    print("\n")
    time.sleep(1)
    client.publish(topic, message)
    print("\n")
    print("已发送消息：" + message)
    timer = threading.Timer(timeout, on_timeout)
    timer.start()

# 消息接收
def on_message(client, userdata, msg):
    global timer
    try:
        payload = msg.payload.decode('utf-8', errors='ignore')  # 忽略解码错误
    except UnicodeDecodeError:
        print("无法解码消息内容")
        return

    # 判断消息来源是否是自己
    if payload != message:
        print("\n收到返回：" + str(payload))
        received_message = str(payload)
        if received_message.startswith('G'):  # 判断是否是公告标识号消息
            if timer:
                timer.cancel()  # 取消超时计时器
            compare_version(received_message[1:])  # 去掉'G'进行版本对比

# 失去连接
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("失去连接 %s" % rc)
    # 确保在断开连接后退出程序
    sys.exit()

# 超时处理
def on_timeout():
    print("\n\t————公告信息版本查询超时————")
    create_timeout_file()
    # 确保在超时后断开连接并退出
    client.loop_stop()
    client.disconnect()

# 创建超时文件
def create_timeout_file():
    # 确保目录存在
    directory = os.path.dirname(timeout_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 创建文件
    with open(timeout_file, 'w') as f:
        f.write("公告信息版本查询超时！")

# 版本对比并创建相应文件
def compare_version(received_version):
    # 先删除已存在的文件
    delete_files()

    received_version = received_version.strip()
    try:
        received_version_num = int(received_version)
    except ValueError:
        print("收到的公告标识号格式不正确")
        return

    try:
        current_version_num = int(current_version)
    except ValueError:
        print("当前公告标识号格式不正确")
        return

    # 对比公告标识号
    if received_version_num > current_version_num:
        create_new_version_file(received_version)
        sys.exit()  # 有新版本后退出程序
    elif received_version_num < current_version_num:
        create_up_to_date_file()
        sys.exit()  # 已是最新版本后退出程序
    else:
        create_up_to_date_file()
        sys.exit()  # 已是最新版本后退出程序

# 创建新版本文件
def create_new_version_file(version):
    # 确保目录存在
    directory = os.path.dirname(new_version_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 创建文件
    with open(new_version_file, 'w') as f:
        f.write(version)

    print("\n\n当前公告标识号： " + current_version)

    print("\n发现新公告标识号: " + version)
    print("\n")

# 创建已是最新版本文件
def create_up_to_date_file():
    # 确保目录存在
    directory = os.path.dirname(up_to_date_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 创建文件
    with open(up_to_date_file, 'w') as f:
        f.write("已是最新公告!")

    print("\n\n当前公告标识号： " + current_version)
    print("\n已是最新公告!")
    print("\n")

global timer
timer = None

client = mqtt.Client(client_id=client_id)
client.username_pw_set("UserName", "Passwd")
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
client.connect(HOST, PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("程序被用户中断")
    client.disconnect()
except Exception as e:
    print(f"发生错误: {e}")
    client.disconnect()
finally:
    print("\n\t客户端已断开连接\n\n")
    sys.exit()