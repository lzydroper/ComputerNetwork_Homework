import sys
import subprocess
import time



if __name__ == "__main__":
    license = input("请输入许可证: ").strip()
    count = int(input("请输入并发数: ").strip())

    proces = []
    for i in range(count):
        cmd = [sys.executable, "client.py", license, "auto"]
        p = subprocess.Popen(cmd)
        proces.append(p)
        time.sleep(0.5)