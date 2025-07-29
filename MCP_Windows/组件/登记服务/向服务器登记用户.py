import paho.mqtt.client as mqtt
import time
import os
import threading
import sys

# 巴法云连接设置
HOST = "bemfa.com"
PORT = 9501
client_id = "ac9a9f2b686bb4257867806c1dcfaf67"  # 使用实际的客户端ID
username = "your_username"  # 替换为你的用户名
password = "your_password"  # 替换为你的密码
topic = "MCPToolsUsers004"  # 定义主题

SUCCESS_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\登记服务\状态\登记成功！.EXE"  # 登记成功状态文件路径
SYSTEM_RECORD_FILE = r"C:\Windows\System32\drivers\etc\用户在服务器登记成功.DLL"  # 在系统登记文件路径
FAILURE_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\登记服务\状态\登记失败！.EXE"  # 登记失败状态文件路径
CHAOSHI_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\登记服务\状态\响应超时！.EXE"  # 登记失败状态文件路径


# 超时时间
TIMEOUT = 5  # 超时时间（秒）

# 全局变量
timer = None
received_message = False
client = None  # 将 client 设置为全局变量
Send_MSG = None  # 用于存储发送的消息


Send_MSG = "请求登记用户！"

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("\n\t连接成功！")
    else:
        print(f"\n\t连接失败，错误码：{rc}")
        sys.exit()

# 消息接收回调
def on_message(client, userdata, msg):
    global received_message
    try:
        payload = msg.payload.decode('utf-8')
    except UnicodeDecodeError:
        print("无法解码消息内容")
        return

    print(f"\n\t收到响应：{payload}")

    # 忽略自己发送的消息
    if payload == Send_MSG:
        print("\n\t忽略自己发送的消息")
        return

    if "登记成功！" in payload:
        # 创建登记成功文件
        with open(SUCCESS_FILE, 'w') as f:
            f.write("登记成功！")
        print(f"\n\t已创建文件：{SUCCESS_FILE}")
        # 创建系统登记成功文件
        with open(SYSTEM_RECORD_FILE, 'w') as f:
            f.write("登记成功！")
        print(f"\n\t已创建文件：{SYSTEM_RECORD_FILE}")


    elif "登记失败！" in payload:
        # 创建登记失败文件
        with open(FAILURE_FILE, 'w') as f:
            f.write("登记失败！")
        print(f"\n\t已创建文件：{FAILURE_FILE}")
    else:
        print("\n\t未知响应，未创建状态文件。")

    received_message = True
    if timer:
        timer.cancel()
    client.loop_stop()
    client.disconnect()
    sys.exit()

# 失去连接回调
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"\n\t失去连接，错误码：{rc}")
    sys.exit()

# 超时处理
def on_timeout():
    global received_message
    if not received_message:
        print("\n\t请求超时，未收到响应！登记失败！")
        with open(CHAOSHI_FILE, 'w') as f:
            f.write("请求超时，未收到响应！登记失败！")
        print(f"\n\t已创建文件：{CHAOSHI_FILE}")
        global client
        if client:
            client.loop_stop()
            client.disconnect()
        sys.exit()

# 主函数
def main():
    global timer
    global client  # 引用全局变量 client
    global Send_MSG  # 引用全局变量 Send_MSG

    # 删除已存在的状态文件
    for file_path in [SUCCESS_FILE, FAILURE_FILE, CHAOSHI_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"\n\t已删除文件：{file_path}")

    # 初始化 MQTT 客户端
    client = mqtt.Client(client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(HOST, PORT, 60)
        print(f"\n\t正在连接到 {HOST}:{PORT}...")
    except Exception as e:
        print(f"\n\t连接失败：{e}")
        sys.exit()

    # 订阅主题
    client.subscribe(topic)

    # 发送登记请求
    client.publish(topic, Send_MSG)
    print(f"\n\t已发送请求：{Send_MSG}")

    # 启动超时定时器
    timer = threading.Timer(TIMEOUT, on_timeout)
    timer.start()

    # 启动消息循环
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\t程序被用户中断")
        client.disconnect()
    except Exception as e:
        print(f"\n\t发生错误：{e}")
        client.disconnect()
    finally:
        print("\n\t客户端已断开连接")

if __name__ == "__main__":
    main()