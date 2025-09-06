import numpy as np
import cv2 as cv
import os

# 定义颜色表，为保证上下一致，修改为黑1，白0
color_map = [
    (255, 255, 255),  # 0: 白色
    (0, 0, 0),        # 1: 黑色
    (0, 0, 255),      # 2: 红色
    (255, 0, 0),      # 3: 蓝色
    (0, 255, 0),      # 4: 绿色
    (128, 0, 128),    # 5: 紫色
    (0, 255, 255),    # 6: 黄色
    (255, 255, 0)     # 7: 青色
]

def read_binary_file(filepath, file_limit = 2048):
    """读取一个限定大小以下的二进制文件并转化为字节列表"""
    file_size = os.path.getsize(filepath)
    assert file_size <= file_limit, f"file size must less than {file_limit}b, file {filepath} is {file_size}"

    with open(filepath, 'rb') as f:
        byte_data = f.read()

    bits = []
    for byte in byte_data:
        # 将每个字节转换为8位二进制，确保高位在前，保证还原后的值与原始字节一致
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    
    if len(bits) % 3 != 0:
        bits += [0] * (3 - len(bits) % 3)

    # 每3位拼一个0-7的数
    data = []
    for i in range(0, len(bits), 3):
        val = (bits[i] << 2) | (bits[i+1] << 1) | bits[i+2]
        data.append(val)
    return data

def bytes_to_img(bytes, output_path, square_size = 10, sqpr = 128):
    """将字节列表转换为sqpr * sqpr方块图像"""

    total_bytes_needed = sqpr * sqpr
    bytes_count = len(bytes)
    if bytes_count < total_bytes_needed:
        bytes += [0] * (total_bytes_needed - bytes_count)   # 为保证上下一致，修改为黑1，白0
    
    image_size = sqpr * square_size

    image = np.full((image_size, image_size, 3), color_map[0], dtype = np.uint8)
    # 填充每个方块
    for i in range(sqpr):  # 行
        for j in range(sqpr):  # 列
            idx = i * sqpr + j
            byte = bytes[idx]
            
            # 计算方块位置
            start_x = j * square_size
            start_y = i * square_size
            end_x = start_x + square_size
            end_y = start_y + square_size
            
            image[start_y:end_y, start_x:end_x] = color_map[byte]
    
    # 保存图像
    cv.imwrite(output_path, image)
    print(f"图像已保存至: {os.path.abspath(output_path)}")

def main():
    bytes = read_binary_file("test.txt")
    bytes_to_img(bytes, "test_color_bin2img.png")

if __name__ == "__main__":
    main()