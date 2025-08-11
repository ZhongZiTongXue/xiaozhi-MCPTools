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



#判断文件区分不同通道

血继限界权所有=r"C:\xiaozhi\MCP\MCP_Windows\血继限界版权所有.INI"
XYZ电子实验室版权所有=r"C:\xiaozhi\MCP\MCP_Windows\XYZ电子实验室版权所有.INI"
Teng版权所有=r"C:\xiaozhi\MCP\MCP_Windows\Teng版权所有.INI"

if os.path.exists(血继限界权所有):
    
    topic = "MCPToolsAK0"  # 定义主题

if os.path.exists(XYZ电子实验室版权所有):
    
    topic = "MCPToolsAK3"  # 定义主题

if os.path.exists(Teng版权所有):
    
    topic = "MCPToolsAK2"  # 定义主题

else:

    topic = "MCPToolsAK0"  # 定义主题


# 激活码文件和状态文件路径
ACTIVATION_CODE_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\激活服务\数据\请求验证的激活码.D"  # 激活码文件路径

SUCCESS_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\激活服务\状态\激活成功！.EXE"  # 激活成功状态文件路径
FAILURE_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\激活服务\状态\激活码无效！.EXE"  # 激活失败状态文件路径
CHAOSHI_FILE = r"C:\xiaozhi\MCP\MCP_Windows\组件\激活服务\状态\响应超时！.EXE"  # 激活失败状态文件路径


# 超时时间
TIMEOUT = 5  # 超时时间（秒）

# 全局变量
timer = None
received_message = False
client = None  # 将 client 设置为全局变量
sent_message = None  # 用于存储发送的消息

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
    if payload == sent_message:
        print("\n\t忽略自己发送的消息")
        return

    if "激活成功！" in payload:
        # 创建激活成功文件
        with open(SUCCESS_FILE, 'w') as f:
            f.write("激活成功！")
        print(f"\n\t已创建文件：{SUCCESS_FILE}")
    elif "此激活码无效！" in payload:
        # 创建激活失败文件
        with open(FAILURE_FILE, 'w') as f:
            f.write("此激活码无效！")
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
        print("\n\t请求超时，未收到响应！")
        with open(CHAOSHI_FILE, 'w') as f:
            f.write("请求超时，未收到响应！")
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
    global sent_message  # 引用全局变量 sent_message

    # 删除已存在的状态文件
    for file_path in [SUCCESS_FILE, FAILURE_FILE, CHAOSHI_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"\n\t已删除文件：{file_path}")

    # 检查激活码文件是否存在
    if not os.path.exists(ACTIVATION_CODE_FILE):
        print(f"\n\t激活码文件不存在：{ACTIVATION_CODE_FILE}")
        sys.exit()

    # 读取激活码
    with open(ACTIVATION_CODE_FILE, 'r') as f:
        activation_code = f.read().strip()

    print(f"\n\t读取激活码：{activation_code}")

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

    # 发送激活请求
    sent_message = f"请求验证激活：{activation_code}"
    client.publish(topic, sent_message)
    print(f"\n\t已发送请求：{sent_message}")

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