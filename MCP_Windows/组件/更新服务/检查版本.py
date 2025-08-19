

import paho.mqtt.client as mqtt
import time
import os
import threading
import sys  # 导入 sys 模块

HOST = "bemfa.com"
PORT = 9501
client_id = "ac9a9f2b686bb4257867806c1dcfaf67"  


#判断文件区分不同通道

粽子同学版权所有=r"C:\xiaozhi\MCP\MCP_Windows\粽子同学版权所有.INI"
血继限界权所有=r"C:\xiaozhi\MCP\MCP_Windows\血继限界版权所有.INI"
XYZ电子实验室版权所有=r"C:\xiaozhi\MCP\MCP_Windows\XYZ电子实验室版权所有.INI"
Teng版权所有=r"C:\xiaozhi\MCP\MCP_Windows\Teng版权所有.INI"

topic = "MCPToolsVersion004"  # 定义主题

if os.path.exists(粽子同学版权所有):
    
    topic = "MCPToolsVersion004"  # 定义主题

if os.path.exists(血继限界权所有):
    
    topic = "MCPToolsVersion0"  # 定义主题

if os.path.exists(XYZ电子实验室版权所有):
    
    topic = "MCPToolsVersion3"  # 定义主题

if os.path.exists(Teng版权所有):
    
    topic = "MCPToolsVersion2"  # 定义主题



message = "请求新版本"

timeout = 10  # 超时时间（秒）
timeout_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\状态\响应超时.exe"
new_version_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\状态\有新版本.exe"
up_to_date_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\状态\已是最新.exe"

# 当前版本
current_version = "48.56.23"

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
        if received_message.startswith('v'):  # 判断是否是版本号消息
            if timer:
                timer.cancel()  # 取消超时计时器
            compare_version(received_message[1:])  # 去掉'v'进行版本对比

# 失去连接
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("失去连接 %s" % rc)
    # 确保在断开连接后退出程序
    sys.exit()

# 超时处理
def on_timeout():
    print("\n\t————版本查询超时————")
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
        f.write("版本查询超时！")

# 版本对比并创建相应文件
def compare_version(received_version):
    # 先删除已存在的文件
    delete_files()

    received_version = received_version.strip()
    current_version_array = current_version.split(".")
    received_version_array = received_version.split(".")

    # 确保版本号格式一致
    if len(current_version_array) != len(received_version_array):
        print("版本格式不一致")
        return

    # 对比版本号
    for i in range(len(current_version_array)):
        if int(received_version_array[i]) > int(current_version_array[i]):
            create_new_version_file(received_version)
            sys.exit()  # 有新版本后退出程序
            return
        elif int(received_version_array[i]) < int(current_version_array[i]):
            create_up_to_date_file()
            sys.exit()  # 已是最新版本后退出程序
            return

    # 如果所有部分都相等
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

    print("\n\n当前版本： " + current_version)

    print("\n发现新版本: " + version)
    print("\n")

# 创建已是最新版本文件
def create_up_to_date_file():
    # 确保目录存在
    directory = os.path.dirname(up_to_date_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 创建文件
    with open(up_to_date_file, 'w') as f:
        f.write("已是最新版本!")

    print("\n\n当前版本： " + current_version)
    print("\n已是最新版本!")
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