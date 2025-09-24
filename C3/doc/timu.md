### 题目：

25. 设有 2 个消息序列 const unsigned char *a, *b;，每个元素为 0 或者非 0（非 0 表示 1） ，<br/>请以：统计时分多路复用、同步时分多路复用、频分多路复用和码分多路复用的方式，<br/>将其合并其为一个完整的信号序列，再将其多路解复用为原始的序列。

    接口： int multiplex(unsigned char *c, const int c_size, const unsigned char *a, const int a_len, const unsigned char *b, const int b_len); 和 int demultiplex(unsigned char *a, const int a_size, unsigned char *b, const int b_size, const unsigned char *c, const int c_len);。

26. 请生成一个正弦波作为载体信号、调制信号（分模拟的和数字等两种） ，生成频带信号（调频、调幅和调相等三种）。<br/>可参考课件“调制：调制信号为模拟信号”和“调制：调制信号为数字信号”两页。

    接口： int generate_cover_signal(unsigned double *cover, c onst int size);； int simulate_digital_modulation_signal (unsigned char *message, const int size);； int simulate_ analog_modulation_signal(unsigned double *message, const int size);； int modulate_digital_frequency (unsigned do uble *cover, const int cover_len, const unsigned char *m essage, const int msg_len);； int modulate_analog_frequen cy(unsigned double *cover, const int cover_len, const un signed double *message, const int msg_len);； int modulat e_digital_amplitude(unsigned double *cover, const int co ver_len, const unsigned char *message, const int msg_le n);； int modulate_analog_amplitude(unsigned double *cove r, const int cover_len, const unsigned double *message, const int msg_len);； int modulate_digital_ phase(unsigned double *cover, const int cover_len, const unsigned char *message, const int msg_len);； int modulate_analog_ phas e(unsigned double *cover, const int cover_len, const uns igned double *message, const int msg_len);。