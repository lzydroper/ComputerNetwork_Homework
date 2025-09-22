

def multiplex(a:str, b:str, type:int) -> str:
    """
    参数：
        a: 输入信号1
        b: 输入信号2
        type: 复用类型
    返回：
        c(str): 合成信号
    """
    # 转化为01字符串
    a_bin = ''.join(['0' if char == 0 else '1' for char in a])
    b_bin = ''.join(['0' if char == 0 else '1' for char in b])


    def extract_block(src:str, size:int, padc='0') -> list[str]:
        """
        切分为组 不足补padc
        """
        blocks = []
        for i in range(0, len(src), size):
            block = src[i:i+size]
            block += padc * (size - len(block))
            blocks.append(block)
        return blocks
    

    def atdm():
        """
        统计时分复用 按字节成块 每个信号源每次取7位 首位为0表示a 首位为1表示b 长度不足补0
        """
        a_blocks = extract_block(a_bin, 7)
        b_blocks = extract_block(b_bin, 7)
        ai = 0
        bi = 0
        result = []
        # 轮询加入
        while ai < len(a_blocks) and bi < len(b_blocks):
            if ai < len(a_blocks):
                block = '0' + a_blocks[ai]
                block_int = int(block, 2)
                block_chr = chr(block_int)
                result.append(block_chr)
                ai += 1
            if bi < len(b_blocks):
                block = '1' + b_blocks[bi]
                block_int = int(block, 2)
                block_chr = chr(block_int)
                result.append(block_chr)
                bi += 1
        return ''.join(result)
    

    def stdm():
        """
        同步时分复用 按字节成块 偶数块为a 奇数块为b 空白块为全0
        """
        a_blocks = extract_block(a_bin, 8)
        b_blocks = extract_block(b_bin, 8)
        empty_block = chr(0)
        result = []
        size = max(len(a_blocks), len(b_blocks))
        for i in range(size):
            if i < len(a_blocks):
                block_int = int(a_blocks[i], 2)
                block_chr = chr(block_int)
                result.append(block_chr)
            else:
                result.append(empty_block)
            
            if i < len(b_blocks):
                block_int = int(b_blocks[i], 2)
                block_chr = chr(block_int)
                result.append(block_chr)
            else:
                result.append(empty_block)

        return ''.join(result)
    

    def fdm():
        """
        频分多路复用 按字节成块 高四位为a 低四位为b  长度不足设置为0
        """
        a_blocks = extract_block(a_bin, 4)
        b_blocks = extract_block(b_bin, 4)
        empty_block = "0000"
        result = []
        size = max(len(a_blocks), len(b_blocks))
        for i in range(size):
            if i < len(a_blocks):
                a_block_chr = a_blocks[i]
            else:
                a_block_chr = empty_block
            
            if i < len(b_blocks):
                b_block_chr = b_blocks[i]
            else:
                b_block_chr = empty_block

            block_int = int(a_block_chr + b_block_chr, 2)
            block_chr = chr(block_int)
            result.append(block_chr)

        return ''.join(result)
    

    def cdm():
        """
        码分多路复用 码片设定为10 11 补0
        """
        import numpy as np
        # 补长
        size = max(len(a_bin), len(b_bin))
        a_bin_padded = a_bin + '0' * (size - len(a_bin))
        b_bin_padded = b_bin + '0' * (size - len(b_bin))
        # 转换为向量
        a_bit = np.array([1 if char == '1' else -1 for char in a_bin_padded])
        b_bit = np.array([1 if char == '1' else -1 for char in b_bin_padded])
        # 拓频
        a_code = np.array([+1, -1])
        b_code = np.array([+1, +1])
        a_s = np.concatenate([b * a_code for b in a_bit])
        b_s = np.concatenate([b * b_code for b in b_bit])
        # 复用
        result = a_s + b_s
        return ' '.join(str(num) for num in result)
    
    
    match type:
        case 0:
            return atdm()
        case 1:
            return stdm()
        case 2:
            return fdm()
        case 3:
            return cdm()
    

def demultiplex(a_size:int, b_size:int, c:str, type:int) -> tuple[str, str]:
    """
    参数：
        a_size: 原信号a长度
        b_size: 原信号b长度
        c: 待解复用的信号
        type: 复用类型
    返回：
        a(str): 信号a
        b(str): 信号b
    """
    def atdm():
        """
        统计tdm 对每个字节转为二进制str 判断首位并分配给两个信号
        """
        a_arr = []
        b_arr = []
        for char in c:
            bin_str = format(ord(char), '08b')
            if bin_str[0] == '0':
                a_arr.append(bin_str[1:])
            else:
                b_arr.append(bin_str[1:])
        # 截取长度
        a = ''.join(a_arr)
        b = ''.join(b_arr)
        return a[:a_size], b[:b_size]


    def stdm():
        """
        同步时分复用 对每个字节先判定是否为0 非零转二进制str
        """
        a_arr = []
        b_arr = []
        for i in range(0, len(c), 2):
            chara, charb = c[i], c[i+1]
            if ord(chara) != 0:
                bin_str = format(ord(chara), '08b')
                a_arr.append(bin_str)
            if charb != 0:
                bin_str = format(ord(charb), '08b')
                b_arr.append(bin_str)
        # 截取长度
        a = ''.join(a_arr)
        b = ''.join(b_arr)
        return a[:a_size], b[:b_size]


    def fdm():
        """
        频分多路复用 对每个字节转为二进制str 高四位为a 低四位为b
        """
        a_arr = []
        b_arr = []
        for char in c:
            bin_str = format(ord(char), '08b')
            a_arr.append(bin_str[:4])
            b_arr.append(bin_str[-4:])
        # 截取长度
        a = ''.join(a_arr)
        b = ''.join(b_arr)
        return a[:a_size], b[:b_size]


    def cdm():
        """
        码分多路复用 码片设定为10 11
        """
        import numpy as np
        c_int = np.array([int(num) for num in c.split()])
        a_code = np.array([+1, -1])
        b_code = np.array([+1, +1])
        a_arr = []
        b_arr = []
        for i in range(0, len(c_int), 2):
            block = c_int[i:i+2]
            a_c = np.dot(block, a_code)
            b_c = np.dot(block, b_code)
            a_arr.append('1' if a_c > 0 else '0')
            b_arr.append('1' if b_c > 0 else '0')
        # 截取长度
        a = ''.join(a_arr)
        b = ''.join(b_arr)
        return a[:a_size], b[:b_size]
    

    match type:
        case 0:
            return atdm()
        case 1:
            return stdm()
        case 2:
            return fdm()
        case 3:
            return cdm()


def format_for_display(s: str) -> list[str]:
    """将字符串逐字符转换为8位二进制字符串数组"""
    binary_array = []
    for char in s:
        # 将字符的ASCII码转换为8位二进制，不足8位前面补0
        binary_str = format(ord(char), '08b')
        binary_array.append(binary_str)
    return binary_array


# 测试函数
def test_multiplex_demultiplex():
    # 测试数据
    test_cases = [
        # (a信号, b信号, 复用类型)
        ([1,0,1,0,1,0,1,0,1], [1,1,0,0,1,1,0,0], 0, "101010101", "11001100"),  # ATDM
        ([1,0,1,0,1,0,1,0], [1,1,0,0,1,1,0,0], 1, "10101010", "11001100"),   # STDM
        ([1,0,1,0,1,0,1,0], [1,1,0,0,1,1,0,0], 2, "10101010", "11001100"),   # FDM
        ([1,0,1,0,1,0], [1,1,0,0], 3, "101010", "1100")          # CDM
    ]
    
    for a, b, type, a_s, b_s in test_cases:
        print(f"\n测试复用类型 {type}:")
        print(f"原始信号 a: {a_s} (长度: {len(a_s)})")
        print(f"原始信号 b: {b_s} (长度: {len(b_s)})")
        
        # 复用
        multiplexed = multiplex(a, b, type)
        # 对CDM特殊处理，其他类型使用格式化显示
        if type == 3:
            print(f"复用后: {multiplexed}")
        else:
            print(f"复用后 (可打印格式): {format_for_display(multiplexed)}")
            print(f"复用后长度: {len(multiplexed)} 字符")
        
        # 解复用
        a_recovered, b_recovered = demultiplex(len(a), len(b), multiplexed, type)
        print(f"解复用后 a: {a_recovered} (长度: {len(a_recovered)})")
        print(f"解复用后 b: {b_recovered} (长度: {len(b_recovered)})")
        
        # 验证结果
        a_match = (a_recovered == a_s)
        b_match = (b_recovered == b_s)
        print(f"a 恢复成功: {a_match}")
        print(f"b 恢复成功: {b_match}")


# 运行测试
if __name__ == "__main__":
    test_multiplex_demultiplex()
