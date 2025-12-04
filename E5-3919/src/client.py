import tkinter as tk
from tkinter import messagebox
import socket
import uuid
import threading
import time

# socket 配置
HOST = '127.0.0.1'
PORT = 39190
BEAT_TIME = 3
RECO_TIME = 5
CONN_TIME = 5

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x200")

        self.client_id = str(uuid.uuid4())[:8]
        self.root.title(f"Client {self.client_id}")
        self.sock = None
        self.is_running = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # layout
        tk.Label(root, text="请输入许可证序列号(10位):").pack(pady=10)
        
        self.entry_sn = tk.Entry(root, font=("Arial", 12))
        self.entry_sn.pack(pady=5)
        
        self.btn_verify = tk.Button(root, text="验证并运行", command=self.start_verification, bg="#dddddd")
        self.btn_verify.pack(pady=15)
        
        self.lbl_status = tk.Label(root, text="状态: 未运行", fg="gray")
        self.lbl_status.pack(pady=5)
    
    def on_closing(self):
        self.is_running = False
        if self.sock:
            try:
                self.sock.send(b"QUIT:")
                self.sock.close()
            except:
                pass
            finally:
                self.sock.close()
        self.root.destroy()

    def start_verification(self):
        self.sn = self.entry_sn.get().strip()
        if not self.sn:
            messagebox.showwarning("提示", "请输入序列号", parent=self.root)
            return
        self.is_running = True
        self.lock_ui()
        t = threading.Thread(target=self.conn_thread)
        t.daemon = True
        t.start()

    def conn_thread(self):
        error_time = 0
        while self.is_running:
            try:
                if self.sock is None:
                    self.login()
                    continue
                    
                self.sock.send(f"BEAT:{self.client_id}".encode())
                response = self.sock.recv(1024).decode()
                if response == "COOL":
                    self.lbl_status.config(text="状态: 运行中 (心跳正常)", fg="green")
                    error_time = 0
                else:
                    raise Exception("Server Error")
                time.sleep(BEAT_TIME)
            except Exception as e:
                error_time += 1
                self.lbl_status.config(text=f"连接断开，正在重连...({error_time}次)", fg="orange")
                if error_time >= 3:
                    messagebox.showwarning("提示", "连接断开，已重试3次，仍失败", parent=self.root)
                    self.is_running = False
                    self.unlock_ui()
                    self.lbl_status.config(text="状态: 未运行", fg="gray")
                    break
                if self.sock:
                    try:
                        self.sock.close()
                    except:
                        pass
                    self.sock = None
                time.sleep(RECO_TIME)


    def login(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(CONN_TIME)
        try:
            self.sock.connect((HOST, PORT))

            msg = f"LOGN:{self.sn}:{self.client_id}"
            self.sock.send(msg.encode())

            response = self.sock.recv(1024).decode()
            if response == "SUCC":
                return
            elif response == "FULL":
                self.lbl_status.config(text="验证失败：人数已满", fg="red")
            else:
                self.lbl_status.config(text="验证失败：未知错误", fg="red")
        except Exception as e:
            messagebox.showwarning("提示", "连接服务器失败", parent=self.root)
        
        self.is_running = False
        self.unlock_ui()

    def lock_ui(self):
        self.entry_sn.config(state='disabled')
        self.btn_verify.config(state='disabled', text="已激活")

    def unlock_ui(self):
        self.entry_sn.config(state='normal')
        self.btn_verify.config(state='normal', text="验证并运行")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    import sys
    if len(sys.argv) > 1:
        auto_sn = sys.argv[1]
        app.entry_sn.insert(0, auto_sn)
        if len(sys.argv) > 2 and sys.argv[2] == "auto":
            app.start_verification()
    root.mainloop()