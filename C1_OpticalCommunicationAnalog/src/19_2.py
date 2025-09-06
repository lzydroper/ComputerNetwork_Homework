import numpy as np
import cv2 as cv

""""""
# 参数列表
image_size = 128
tmp_file = "tmp.png"
# 颜色表
color_map = [
    (0, 0, 0),        # 0: 黑色
    (255, 255, 255),  # 1: 白色
    (0, 0, 255),      # 2: 红色
    (255, 0, 0),      # 3: 蓝色
    (0, 255, 0),      # 4: 绿色
    (128, 0, 128),    # 5: 紫色
    (0, 255, 255),    # 6: 黄色
    (255, 255, 0)     # 7: 青色
]
""""""

def encode(msg : int):
    assert 0 <= msg <= 7, f"msg must be 0 <= msg <= 7, but now : f{msg}"
    image = np.full((image_size, image_size, 3), color_map[msg], dtype=np.uint8)
    cv.imwrite(tmp_file, image)

def decode():
    img = cv.imread(tmp_file, cv.IMREAD_COLOR)
    color = tuple(int(x) for x in img.mean(axis=(0,1)))
    msg = color_map.index(color)
    return msg

encode(5)
print(decode())