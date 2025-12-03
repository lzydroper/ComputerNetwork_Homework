# pcap_logger.py
# Python3, requires scapy and pandas. Run as admin.
from scapy.all import sniff, Ether, IP
import csv
import time
from datetime import datetime
import threading
import collections
import os
import pandas as pd

# 输出文件
LOG_CSV = "pcap_log.csv"
STATS_CSV = "pcap_stats.csv"

# 统计窗口（秒）
STAT_INTERVAL = 60

# 内存存储的统计：按(src_mac, src_ip) 和 (dst_mac, dst_ip) 统计 bytes
sent_counter = collections.Counter()
recv_counter = collections.Counter()
lock = threading.Lock()

def packet_handler(pkt):
    # 只处理以太网帧
    if not pkt.haslayer(Ether):
        return
    try:
        eth = pkt[Ether]
        src_mac = eth.src
        dst_mac = eth.dst
        length = len(pkt)  # 帧长度（字节）
        src_ip = ""
        dst_ip = ""
        if pkt.haslayer(IP):
            ip = pkt[IP]
            src_ip = ip.src
            dst_ip = ip.dst
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 写入日志（追加）
        header_needed = not os.path.exists(LOG_CSV)
        with open(LOG_CSV, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if header_needed:
                writer.writerow(["时间","源 MAC","源 IP","目标 MAC","目标 IP","帧长度"])
            writer.writerow([timestamp, src_mac, src_ip, dst_mac, dst_ip, length])

        # 更新统计（线程安全）
        with lock:
            sent_counter[(src_mac, src_ip)] += length
            recv_counter[(dst_mac, dst_ip)] += length

    except Exception as e:
        # 防止某些包解析异常导致脚本崩溃
        print("解析包出错:", e)

def stats_worker():
    """
    每 STAT_INTERVAL 秒 dump 一次统计，并清空计数（或累积，视需求）
    这里我们把每个时间段的统计写入 CSV（追加）
    """
    while True:
        time.sleep(STAT_INTERVAL)
        with lock:
            # 把当前统计写入文件
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows = []
            for (mac, ip), bytes_sent in sent_counter.items():
                rows.append([now, "SENT", mac, ip, bytes_sent])
            for (mac, ip), bytes_recv in recv_counter.items():
                rows.append([now, "RECV", mac, ip, bytes_recv])

            # 写入 STAT CSV（如果不存在写头）
            header_needed = not os.path.exists(STATS_CSV)
            with open(STATS_CSV, "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if header_needed:
                    writer.writerow(["时间","方向","MAC","IP","字节数"])
                for r in rows:
                    writer.writerow(r)

            # 可选：打印到控制台
            print(f"[{now}] 写入统计: {len(rows)} 条记录")

            # 重置计数器（如果希望累积则注释掉下面两行）
            sent_counter.clear()
            recv_counter.clear()

if __name__ == "__main__":
    # 启动统计线程
    t = threading.Thread(target=stats_worker, daemon=True)
    t.start()

    print("开始抓包。按 Ctrl+C 停止。请以管理员/系统权限运行此脚本。")
    # 若需要指定接口： sniff(iface="以太网", prn=packet_handler, store=False)
    sniff(prn=packet_handler, store=False)
