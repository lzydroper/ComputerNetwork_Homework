



def rs232c_encode(msg : str) -> list[int]:
    """
    字节大端序，位小端序，-3~-15表示1, 3~15表示0, 空闲终止为0, 开始为1
    参数: msg(str)
    返回: list[int], 电压序列
    """
    # 定义高低电平
    v0 = 15
    v1 = -15
    voltages = []
    # 初始为空闲
    voltages.append(v0)
    for char in msg:
        ascii_value = ord(char)
        if ascii_value > 127:
            raise ValueError(f"fuck you {char}'s ascii is {ascii_value} bigger than 127(7 bits)")
        binary_str = bin(ascii_value)[2:].zfill(7)
        reversed_binary_str = binary_str[::-1]
        
        # 添加起始位
        voltages.append(v1)

        for bit in reversed_binary_str:
            if bit == '1':
                voltages.append(v1)
            else:
                voltages.append(v0)

        # 添加终止位
        voltages.append(v0)

    voltages.append(v0)
    return voltages


def rs232c_decode(voltages : list[int]) -> str:
    """
    字节大端序，位小端序，-3~-15表示1, 3~15表示0, 空闲终止为0, 开始为1
    参数: list[int], 电压序列
    返回: msg(str)
    """
    # 定义高低电平
    v0_l = 3
    v0_r = 15
    v1_l = -15
    v1_r = -3
    msg = []
    i = 0
    length = len(voltages)

    # 跳过初始空闲位
    while i < length and voltages[i] >= 3:
        i += 1

    while i < length:
        if v1_l <= voltages[i] <= v1_r:
            i += 1
            
            # 读取7位数据位
            bits = []
            if i + 7 > length:
                raise ValueError("电压序列不完整，缺少数据位")
                
            for _ in range(7):
                if v0_l <= voltages[i] <= v0_r:  # 0
                    bits.append('0')
                elif v1_l <= voltages[i] <= v1_r:  # 1
                    bits.append('1')
                else:
                    raise ValueError(f"fuck you error voltage {voltages[i]} in index {i}")
                i += 1
            
            if i >= length or not v0_l <= voltages[i] <= v0_r:
                raise ValueError("fuck you not end bit")
            i += 1  # 跳过终止位
            
            reversed_bits = ''.join(bits[::-1])
            ascii_value = int(reversed_bits, 2)
            msg.append(chr(ascii_value))
        else:
            i += 1
    
    return ''.join(msg)

if __name__ == "__main__":
    test_str = "Hello, RS232!"
    print(f"原始字符串: {test_str}")
    
    # 编码
    encoded = rs232c_encode(test_str)
    print(f"编码后的电压序列长度: {len(encoded)}")
    print(encoded)
    
    # 解码
    decoded = rs232c_decode(encoded)
    print(f"解码后的字符串: {decoded}")
    
    # 验证编码解码是否一致
    print(f"编码解码是否一致: {test_str == decoded}")