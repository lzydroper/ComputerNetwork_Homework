### 题目：

16. 请编写一个程序，以字节大端序、位小端序，输入一个字母，模拟 RS232C，
以 7-bit 编码方式，包括空闲位、起始位和终止位，输出电压值序列。
接口： int rs232c_encode(double *volts, int volts_size,
const char *msg, int size); int rs232c_decode(char *msg,
int size, const double *volts, int volts_size);。