import paho.mqtt.client as mqtt
import time
import os
import threading
import sys

HOST = "bemfa.com"
PORT = 9501
client_id = "ac9a9f2b686bb4257867806c1dcfaf67"  # 使用实际的客户端ID


#判断文件区分不同通道

粽子同学版权所有=r"C:\xiaozhi\MCP\MCP_Windows\粽子同学版权所有.INI"
血继限界权所有=r"C:\xiaozhi\MCP\MCP_Windows\血继限界版权所有.INI"
XYZ电子实验室版权所有=r"C:\xiaozhi\MCP\MCP_Windows\XYZ电子实验室版权所有.INI"

topic = "MCPToolsVersion004"  # 定义主题

if os.path.exists(粽子同学版权所有):
    
    topic = "MCPToolsVersion004"  # 定义主题

if os.path.exists(血继限界权所有):
    
    topic = "MCPToolsVersion0"  # 定义主题

if os.path.exists(XYZ电子实验室版权所有):
    
    topic = "MCPToolsVersion3"  # 定义主题



message = "请求更新链接"
timeout = 10  # 超时时间（秒）
ota_link_file = r"C:\xiaozhi\MCP\MCP_Windows\组件\更新服务\OTA链接.exe"


# 删除已存在的文件
def delete_files():
    if os.path.exists(ota_link_file):
        os.remove(ota_link_file)


# 连接并订阅
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code " + str(rc))
        client.subscribe(topic)
    else:
        print(f"连接失败，错误码：{rc}")
        sys.exit()


# 订阅成功
def on_subscribe(client, userdata, mid, granted_qos):
    print("订阅成功= %d" % granted_qos)
    print("\n")
    time.sleep(1)
    client.publish(topic, message)
    print("\n")
    print("已发送消息：" + message)
    global timer
    timer = threading.Timer(timeout, on_timeout)
    timer.start()


# 消息接收
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8', errors='ignore')
    except UnicodeDecodeError:
        print("无法解码消息内容")
        return

    if payload != message and payload.startswith('http'):
        print("\n收到返回：" + payload)
        with open(ota_link_file, 'w') as f:
            f.write(payload)
        print("\nOTA链接已保存到文件：" + ota_link_file)
        global timer
        if timer:
            timer.cancel()
        client.loop_stop()
        client.disconnect()
        sys.exit()


# 失去连接
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("失去连接 %s" % rc)
    sys.exit()


# 超时处理
def on_timeout():
    print("\n\t————获取OTA链接超时————")
    with open(ota_link_file, 'w') as f:
        f.write("获取OTA链接超时！")
    client.loop_stop()
    client.disconnect()
    sys.exit()


delete_files()

client = mqtt.Client(client_id=client_id)
client.username_pw_set("UserName", "Passwd")  # 确保替换为实际的用户名和密码
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