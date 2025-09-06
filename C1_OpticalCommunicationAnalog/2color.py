import gray_bin2img as en
import gray_img2bin as de

""""""
# 配置列表
square_size = 32
sqpr = 128   #squares_per_row
file_to_encode = "test.txt"
file_encoded = "encoded.png"
file_to_decode = file_encoded
file_decoded = "decoded.bin"
""""""

def encode(input_file = file_to_encode, output_file = file_encoded):
    file_limit = sqpr * sqpr / 8
    bits = en.read_binary_file(input_file, file_limit)
    en.bits_to_img(bits, output_file, square_size, sqpr)
    pass

def decode(input_file = file_to_decode, output_file = file_decoded):
    binary_img = de.read_img(input_file)
    bits = de.extract_bits(binary_img, square_size, square_size, sqpr, sqpr)
    bits = de.fix_bits(bits)
    de.bits_to_binary_file(bits, output_file)
    pass

def send(filepath = None):
    """将指定文件进行加密（加密某个文件后发送）"""
    if filepath is not None:
        encode(filepath)
    else:
        encode()
    pass

def receive(filepath = None):
    """将指定文件进行解密（将接收的文件翻译）"""
    if filepath is not None:
        decode(filepath)
    else:
        decode()
    pass

def main():
    print(f"send file {file_to_encode} as {file_encoded}")
    send()

    print(f"receive file {file_to_decode} as {file_decoded}")
    receive()

if __name__ == "__main__":
    main()