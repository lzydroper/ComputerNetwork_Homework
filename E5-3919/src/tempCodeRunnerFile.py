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