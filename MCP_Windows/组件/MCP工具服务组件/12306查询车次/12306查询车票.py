import json

import requests

城市代码列表文件路径= r"C:\xiaozhi\12306查询车牌\城市代码列表.json"
k = open(城市代码列表文件路径,encoding='utf-8').read()

#导入伪装信息
User_agent=r"C:\xiaozhi\12306查询车牌\本地伪装信息\User-agent.txt"
Cookie=r"C:\xiaozhi\12306查询车牌\本地伪装信息\Cookie.txt"
Referer=r"C:\xiaozhi\12306查询车牌\本地伪装信息\Referer.txt"


城市代码=json.loads(k)

出发城市=input("请输入出发城市：")
到达城市=input("请输入到达城市：")
出发日期=input("请输入出发日期：")

url =f"https://kyfw.12306.cn/otn/leftTicket/queryU?leftTicketDTO.train_date={出发日期}&leftTicketDTO.from_station={城市代码[出发城市]}&leftTicketDTO.to_station={城市代码[到达城市]}&purpose_codes=ADULT"

headers =  {'user-agent': open(User_agent).read(),
            'cookie': open(Cookie).read(),
            'referer': open(Referer).read()}

#发送请求
res= requests.get(url,headers=headers)

JSON = res.json()

# 将 12306 返回的 result 列表拿出来
trains = JSON['data']['result']
# 车站代码→中文映射
station_map = JSON['data']['map']

seen = set()
count = 0

count = 0
车辆信息 = []          # ① 先建空列表
for raw in trains:
    c = raw.split('|')
    # 不再去重
    count += 1
    from_zh = station_map.get(c[6], c[6])
    to_zh   = station_map.get(c[7], c[7])
    # 固定宽度，左对齐
    print(f"{c[3]:<5} "
            f"{from_zh:<6}→ {to_zh:<6} "
            f"{c[8]} 开 {c[9]} 到 "
            f"历 {c[10]:<5} "
            f"商务 {c[32] or '-':<3} "
            f"一等 {c[31] or '-':<3} "
            f"二等 {c[30] or '-':<3} "
            f"无座 {c[29] or '-'}")

# 打印总趟数
print(f"\n————————————————————————————————————————————————————————————————————————————————————————————")
print(f"\n\t\t\t\t\t共查询到 {count} 趟列车\n\n")
