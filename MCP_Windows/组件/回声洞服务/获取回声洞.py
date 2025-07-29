import paho.mqtt.client as mqtt
import os
import time
import threading
import sys
import colorama
from colorama import Fore, Style
from datetime import datetime

colorama.init(autoreset=True)

# ---------- 配置 ----------
HOST = "bemfa.com"
PORT = 9501
client_id = "ac9a9f2b686bb4257867806c1dcfaf67"
username  = "your_username"
password  = "your_password"
TOPIC     = "HSD004"

TIMEOUT_SECOND = 3
TIMEOUT_FILE   = r"C:\xiaozhi\MCP\MCP_Windows\组件\回声洞服务\数据\请求回声洞超时.exe"
CONTENT_FILE   = r"C:\xiaozhi\MCP\MCP_Windows\组件\回声洞服务\数据\请求到回声洞内容.DLL"

# ---------- 日志 ----------
def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def log(msg, color=Fore.WHITE, to_file=True):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console_line = f"{Fore.CYAN}[{now}]{Style.RESET_ALL} {color}{msg}"
    print(console_line)


def banner(title):
    sep = "=" * 80
    log(sep, to_file=False)
    log(title.center(80), Fore.YELLOW, to_file=False)
    log(sep, to_file=False)

# ---------- 文件管理 ----------
def clear_files():
    for f in (TIMEOUT_FILE, CONTENT_FILE):
        if os.path.exists(f):
            os.remove(f)
            log(f"🗑 已删除旧文件：{f}")

def create_timeout_file():
    ensure_dir(TIMEOUT_FILE)
    with open(TIMEOUT_FILE, "w") as f:
        f.write("回声洞响应超时！")
    log("🚨 超时文件已生成")

def save_content(content: str):
    ensure_dir(CONTENT_FILE)
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    log("💾 内容已保存到：{}".format(CONTENT_FILE))

# ---------- MQTT ----------
class EchoRequestClient:
    def __init__(self):
        self.timer = None
        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    # 连接成功
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log("✅ 已连接巴法云")
            client.subscribe(TOPIC)
            log("📡 已订阅主题：{}".format(TOPIC))
            client.publish(TOPIC, "请求回声洞")
            log("📤 已发送【请求回声洞】")
            self.timer = threading.Timer(TIMEOUT_SECOND, self.on_timeout)
            self.timer.start()
        else:
            log(f"❌ 连接失败，返回码：{rc}", Fore.RED)
            sys.exit()

    # 收到消息
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8', errors='ignore').strip()
        if payload == "请求回声洞":
            return  # 忽略自己发的
        if self.timer:
            self.timer.cancel()
        log("📥 收到回声洞内容：\n\t{}".format(payload), Fore.GREEN)
        save_content(payload)
        client.disconnect()

    # 断开连接
    def on_disconnect(self, client, userdata, rc):
        log("👋 任务完成，断开连接")
        sys.exit()

    # 超时
    def on_timeout(self):
        log("⏰ 3 秒内未收到回声洞，视为超时！", Fore.RED)
        create_timeout_file()
        self.client.disconnect()

    # 启动
    def run(self):
        clear_files()
        banner("回声洞请求客户端启动")
        try:
            self.client.connect(HOST, PORT, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            log("手动中断", Fore.YELLOW)
        except Exception as e:
            log(f"发生错误：{e}", Fore.RED)
        finally:
            self.client.disconnect()

# ---------- 入口 ----------
if __name__ == "__main__":
    EchoRequestClient().run()