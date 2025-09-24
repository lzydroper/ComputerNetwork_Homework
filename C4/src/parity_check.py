

def parity_check(msg, odd=True):
    """
    参数: msg(str), 消息
    返回: int, 0 表示校验失败， 1 表示校验通过
    """
    # 规定8位加1位校验 即长度限定为9
    if odd:
        return 1 if msg.count('1') % 2 == 1 else 0
    else:
        return 1 if msg.count('1') % 2 == 0 else 0

if __name__ == "__main__":
    msg = '101010101'
    print(parity_check(msg))
    print(parity_check(msg, False))