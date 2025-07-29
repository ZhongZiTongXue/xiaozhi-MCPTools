#!/usr/bin/env python3
# update_12306_headers.py
import os
import time
import random
import requests

# ===== 1. 你要保存到的具体目录（改成自己的） =====
SAVE_DIR = r"C:\xiaozhi\MCP\MCP_Windows\组件\MCP工具服务组件\12306查询车次\本地伪装信息"
os.makedirs(SAVE_DIR, exist_ok=True)

UA_FILE    = os.path.join(SAVE_DIR, "User-agent.txt")
COOKIE_FILE = os.path.join(SAVE_DIR, "Cookie.txt")
REFERER_FILE = os.path.join(SAVE_DIR, "Referer.txt")

# ===== 2. 浏览器 UA 池（可自行扩充） =====
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

REFERER = "https://kyfw.12306.cn/otn/leftTicket/init"

def update_headers():
    # 随机 UA
    ua = random.choice(UA_POOL)

    # 领取 Cookie
    session = requests.Session()
    session.headers.update({"User-Agent": ua, "Referer": REFERER})
    resp = session.get(REFERER, timeout=10)
    cookie_parts = [f"{k}={v}" for k, v in session.cookies.items()]
    cookie_str = "; ".join(cookie_parts)

    # 写入文件（覆盖旧文件）
    with open(UA_FILE, "w", encoding="utf-8") as f:
        f.write(ua)
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookie_str)
    with open(REFERER_FILE, "w", encoding="utf-8") as f:
        f.write(REFERER)

    print("已更新 UA / Cookie / Referer 到：")
    print("  UA_FILE    ->", UA_FILE)
    print("  COOKIE_FILE ->", COOKIE_FILE)
    print("  REFERER_FILE ->", REFERER_FILE)
    print("当前 UA：", ua)
    print("当前 Cookie（前 80 字符）：", cookie_str[:80] + ("..." if len(cookie_str) > 80 else ""))

if __name__ == "__main__":
    update_headers()