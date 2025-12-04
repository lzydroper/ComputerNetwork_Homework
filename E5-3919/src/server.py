import socket
import random
import time
import threading
import json
from flask import Flask, request, render_template, redirect, url_for

# socket 配置
HOST = '127.0.0.1'
PORT = 39190
CONN_TIME = 7
RECO_TIME = 10

# server 配置
SERVER_PORT = 39191
SERVER_FILE = "server.json"

# 许可证
max_usrs = 3
licenses = {
    "2023003919": []
}

def save_json():
    with open(SERVER_FILE, "w") as f:
        json.dump(licenses, f)

def load_json():
    global licenses
    try:
        with open(SERVER_FILE, "r") as f:
            licenses = json.load(f)
        for license in licenses:
            for usr in licenses[license]:
                usr["last_beat"] = time.time()
    except FileNotFoundError:
        save_json()
    except Exception as e:
        print(e)



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', new_license=request.args.get('new_license'))

@app.route('/generate', methods=['POST'])
def generate():
    while True:
        license = "".join(random.choices("0123456789", k=10))
        if license not in licenses:
            break
    licenses[license] = []
    save_json()
    return redirect(url_for('index', new_license=license))

@app.route('/watch')
def watch():
    data = {}
    for license, usrs in licenses.items():
        usr_list = ', '.join([usr["addr"] for usr in usrs])
        data[license] = {
            "count": len(usrs),
            "max": max_usrs,
            "users_str": usr_list if usr_list else "None"
        }
    return render_template('watch.html', data=data)



def handle_client_thread(conn, addr):
    conn.settimeout(CONN_TIME)
    license = None
    usr = None
    try:
        while True:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                print(f"Timeout from {addr}")
                break
            except ConnectionResetError:
                print(f"Connection reset by peer from {addr}")
                break

            if not data:
                break
            msg = data.decode().strip()

            if msg.startswith("LOGN:"):
                parts = msg.split(":")
                if len(parts) < 3:
                    conn.send(b"ERRO")
                    continue
                license = parts[1]
                uid = parts[2]
                if license in licenses:
                    # 原用户断线重连
                    old_usr = None
                    for u in licenses[license]:
                        if u["uid"] == uid:
                            old_usr = u
                            break
                    if old_usr:
                        usr = old_usr
                        usr["addr"] = f"{addr[0]}:{addr[1]}"
                        usr["last_beat"] = time.time()
                        conn.send(b"SUCC")
                        save_json()
                    elif len(licenses[license]) < max_usrs:
                        usr = {
                            "uid": uid,
                            "addr": f"{addr[0]}:{addr[1]}", 
                            "last_beat": time.time()
                        }
                        licenses[license].append(usr)
                        conn.send(b"SUCC")
                        save_json()
                    else:
                        conn.send(b"FULL")
                else:
                    conn.send(b"NOPE")
            elif msg.startswith("BEAT:"):
                if usr:
                    usr["last_beat"] = time.time()
                    conn.send(b"COOL")
                else:
                    conn.send(b"NOPE")
            elif msg.startswith("QUIT:"):
                if usr:
                    licenses[license].remove(usr)
                    usr = None
                    conn.send(b"SUCC")
                    save_json()
    except Exception as e:
        print(e)
    finally:
        conn.close()

def clean_thread():
    while True:
        time.sleep(RECO_TIME)
        need_save = False
        for license, usrs in licenses.items():
            now = time.time()
            alive_usrs = [u for u in usrs if now - u["last_beat"] <= CONN_TIME]
            if len(alive_usrs) != len(usrs):
                licenses[license] = alive_usrs
                need_save = True
        if need_save:
            save_json()

def socket_server_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client_thread, args=(conn, addr))
            t.start()

if __name__ == '__main__':
    load_json()
    ct = threading.Thread(target=clean_thread)
    ct.daemon = True
    ct.start()
    t = threading.Thread(target=socket_server_thread)
    t.daemon = True
    t.start()
    app.run(port=SERVER_PORT, debug=False)
    print(f"Server is running on http://{HOST}:{SERVER_PORT}")