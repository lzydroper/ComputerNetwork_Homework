import numpy as np
import cv2 as cv
import os

def read_img(image_path) -> cv.Mat:
    """读取灰度图并二值化"""
    img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)    # 读取灰度图
    assert img is not None, f"file {image_path} could not be read."

    _, binary_img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)  # 二值化
    return binary_img

def detect_grid(binary_img : cv.Mat):
    """划分网格"""
    # # 计算图像中颜色变化的位置，估计方块大小
    # row_changes = np.where(np.diff(binary_img.mean(axis=1) > 127))[0]
    # col_changes = np.where(np.diff(binary_img.mean(axis=0) > 127))[0]
    
    # if len(row_changes) > 1 and len(col_changes) > 1:
    #     square_height = int(np.median(np.diff(row_changes)))
    #     square_width = int(np.median(np.diff(col_changes)))
    # else:
    #     raise ValueError(f"could not detect grid size, \
    #                      len(row_changes) is {len(row_changes)}, \
    #                         len(col_changes) is {len(col_changes)}")
        
    # height, width = binary_img.shape
    # rows = height // square_height
    # cols = width // square_width
    # ！！！应该规定rows和cols的值，然后定位计算小方块的大小！！！
    square_height = square_width = 10
    rows = cols = 128
    
    return square_height, square_width, rows, cols

def extract_bits(binary_img : cv.Mat, square_height, square_width, rows, cols):
    """提取比特"""
    bits = []
    height, width = binary_img.shape

    # 先假定图像规整，从0,0开始
    start_y = 0
    start_x = 0

    for y in range(rows):
        for x in range(cols):
            # 计算当前方块的位置
            top = start_y + y * square_height
            bottom = top + square_height
            left = start_x + x * square_width
            right = left + square_width
            
            # 确保不超出图像边界
            bottom = min(bottom, height)
            right = min(right, width)
            
            # 提取方块区域
            square = binary_img[top:bottom, left:right]
            
            # 计算区域内的平均亮度
            avg_val = np.mean(square)
            
            # 黑色(0)表示1，白色(255)表示0
            bit = 1 if avg_val < 127 else 0
            bits.append(bit)
    
    return bits#, rows, cols

def fix_bits(bits):
    """截断提取出来的多余的部分"""
    if not bits or 1 not in bits:
        return []  # 全0或者空数组 → 返回空
    
    last_one_index = len(bits) - 1 - bits[::-1].index(1)  # 找最后一个1的位置
    return bits[:last_one_index + 1]

def format_bits_for_printing(bits, bits_per_group=8, groups_per_line=4):
    """格式化比特流用于打印输出"""
    groups = [bits[i:i+bits_per_group] for i in range(0, len(bits), bits_per_group)]
    
    formatted_lines = []
    for i in range(0, len(groups), groups_per_line):
        line_groups = groups[i:i+groups_per_line]
        line_str = '   '.join([''.join(map(str, g)) for g in line_groups])
        formatted_lines.append(line_str)
    
    return '\n'.join(formatted_lines)

def bits_to_binary_file(bits, output_file):
    """将比特流转换为二进制文件"""
    # 确保比特数量是8的倍数
    remainder = len(bits) % 8
    if remainder != 0:
        bits += [0] * (8 - remainder)
        print(f"警告: 比特数量不是8的倍数，已填充{8 - remainder}个0使其完整")
    
    # 转换为字节
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        byte_value = 0
        for bit in byte_bits:
            byte_value = (byte_value << 1) | bit
        bytes_data.append(byte_value)
    
    # 写入文件
    with open(output_file, 'wb') as f:
        f.write(bytes_data)
    
    print(f"二进制文件已保存至: {os.path.abspath(output_file)}")

def main():
    image_path = "grid_pattern.png"  # 替换为你的图像路径
    output_file = "grid_output.bin"
    
    try:
        # 读取图像
        binary_img = read_img(image_path)
        
        # 划分网格
        square_h, square_w, rows, cols = detect_grid(binary_img)
        print(f"检测到网格: {rows}行 x {cols}列，方块大小: {square_h}x{square_w}")
        
        # 提取比特
        # bits, rows, cols = extract_bits(binary_img, square_h, square_w, rows, cols)
        bits = extract_bits(binary_img, square_h, square_w, rows, cols)
        bits = fix_bits(bits)
        print(f"成功提取 {len(bits)} 个比特")
        
        # # 格式化输出
        # print()
        # print("比特流输出:")
        # print(format_bits_for_printing(bits))
        
        # 保存为二进制文件
        bits_to_binary_file(bits, output_file)
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

if __name__ == "__main__":
    main()