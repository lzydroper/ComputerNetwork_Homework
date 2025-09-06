import numpy as np
import cv2 as cv

"""
黑表示0, 白表示1
"""

""""""
# 参数列表
image_size = 128
tmp_file = "tmp.png"
""""""

def encode(msg : int):
    assert (msg == 0 or msg == 1), f"msg must be 0 or 1, but now : f{msg}"
    image = np.ones((image_size, image_size), dtype=np.uint8) * 255 * msg
    cv.imwrite(tmp_file, image)

def decode():
    img = cv.imread(tmp_file, cv.IMREAD_GRAYSCALE)
    msg = int(img.mean(axis=(0, 1)) / 255)
    return msg

encode(0)
print(decode())