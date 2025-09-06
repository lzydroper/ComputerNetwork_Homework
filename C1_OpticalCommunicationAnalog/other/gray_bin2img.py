import numpy as np
import cv2 as cv
import os

def read_binary_file(filepath, file_limit = 2048):
    """读取一个限定大小以下的二进制文件并转化为比特列表"""
    file_size = os.path.getsize(filepath)
    assert file_size <= file_limit, f"file size must less than {file_limit}b, file {filepath} is {file_size}"

    with open(filepath, 'rb') as f:
        byte_data = f.read()

    # 转换为比特列表
    bits = []
    for byte in byte_data:
        # 将每个字节转换为8位二进制，确保高位在前，保证还原后的值与原始字节一致
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    
    return bits

def bits_to_img(bits, output_path, square_size = 10, sqpr = 128):
    """将比特列表转换为sqpr * sqpr方块图像"""
    # 网格总比特数
    total_bits_needed = sqpr * sqpr
    bits_count = len(bits)
    
    # 如果比特数不足，用0填充；如果超过，截断
    if bits_count < total_bits_needed:
        bits += [0] * (total_bits_needed - bits_count)
        print(f"警告: 输入数据不足，已填充{total_bits_needed - bits_count}个0")
    elif bits_count > total_bits_needed:
        bits = bits[:total_bits_needed]
        print(f"警告: 输入数据过多，已截断至{total_bits_needed}个比特")

    # 计算图像尺寸
    image_size = sqpr * square_size
    
    # 创建白色背景图像（255）
    image = np.ones((image_size, image_size), dtype=np.uint8) * 255

    # 填充每个方块
    for i in range(sqpr):  # 行
        for j in range(sqpr):  # 列
            bit_index = i * sqpr + j
            bit = bits[bit_index]
            
            # 计算方块位置
            start_x = j * square_size
            start_y = i * square_size
            end_x = start_x + square_size
            end_y = start_y + square_size
            
            # 黑色表示1，白色表示0
            if bit == 1:
                image[start_y:end_y, start_x:end_x] = 0  # 黑色
    
    # 保存图像
    cv.imwrite(output_path, image)
    print(f"图像已保存至: {os.path.abspath(output_path)}")

def main():
    # input_file = "test.bmp"    # 输入二进制文件路径
    input_file = input("please input a input_file name with suffix: ")
    output_file = "grid_pattern.png"  # 输出图像路径
    square_size = 10            # 每个小方块的像素大小
    
    try:
        # 读取二进制文件并转换为比特
        bits = read_binary_file(input_file)
        print(f"成功读取 {len(bits)} 个比特")
        
        # 转换为128x128网格图像
        bits_to_img(bits, output_file, square_size)
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

if __name__ == "__main__":
    main()