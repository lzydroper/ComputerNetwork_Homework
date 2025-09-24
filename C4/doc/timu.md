### \9. 编写一个检验奇偶校验码的程序。其中，消息 msg 的每个元素限于 0 和非 0（表示 1）两种，返回值： 0 表示校验失败， 1 表示校验通过。

接口： int parity_check(const unsigned char *msg, const int msg_length);  