from scapy.all import sniff, Ether, IP
from datetime import datetime
import csv, collections, os

LOG_CSV = "pcap_log.csv"
STATS_CSV = "pcap_stats.csv"

def pcap(cycles, timeout):
    for cycle in range(cycles):
        # 抓包
        print(f"第{cycle+1}轮抓包中...")
        packets = sniff(timeout=timeout)
        log_rows = []
        counter = collections.Counter()
        for pkt in packets:
            if not pkt.haslayer(Ether): continue
            eth = pkt[Ether]
            src_mac = eth.src
            dst_mac = eth.dst
            length = len(pkt)
            src_ip, dst_ip = "", ""
            if pkt.haslayer(IP):
                ip = pkt[IP]
                src_ip, dst_ip = ip.src, ip.dst
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_rows.append([t, src_mac, src_ip, dst_mac, dst_ip, length])
            counter[(src_ip, dst_ip)] += length
        # 写日志
        header_needed = not os.path.exists(LOG_CSV)
        with open(LOG_CSV, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if header_needed:
                writer.writerow(["时间","源 MAC","源 IP","目标 MAC","目标 IP","帧长度"])
            writer.writerows(log_rows)
        # 写统计
        header_needed = not os.path.exists(STATS_CSV)
        with open(STATS_CSV, "a", newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if header_needed:
                w.writerow(["时间","源 IP","目标 IP","字节数"])
            for k,v in counter.items():
                w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), *k, v])
        print(f"第{cycle+1}轮抓包完成，记录{len(log_rows)}个包。")


if __name__ == "__main__":
    pcap(2, 60)