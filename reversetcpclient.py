import socket
import random
import sys
import struct

# TCP客户端类
class TCPClient:
    # 初始化客户端，连接服务器
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip  # 服务器IP地址
        self.server_port = server_port  # 服务器端口
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字
        self.client_socket.connect((self.server_ip, self.server_port))  # 连接服务器

    # 运行客户端，读取文件，发送数据块并接收反转后的数据
    def run(self, path, Lmin, Lmax):
        with open(path, 'r') as file:
            data = file.read()  # 读取文件内容

        blocks = []  # 初始化块列表，用于存储分块后的数据
        current_pos = 0  # 初始化当前读取位置
        length = len(data)  # 获取数据的总长度

        # 将数据分块处理，块大小在Lmin和Lmax之间随机
        while current_pos < length:
            block_size = random.randint(Lmin, Lmax)  # 随机确定块大小
            if current_pos + block_size >= length:
                # 如果块大小超出文件末尾，则读取到文件末尾
                blocks.append(data[current_pos:length])
            else:
                # 否则，读取当前块数据
                blocks.append(data[current_pos:current_pos + block_size])
            current_pos += block_size  # 更新当前读取位置

        # 发送初始化报文，包含报文类型和块计数
        # 报文类型1表示初始化报文，块计数表示后续将要发送的数据块数量
        initialization = struct.pack('!HI', 1, len(blocks))
        self.client_socket.sendall(initialization)  # 发送初始化报文到服务器

        # 接收服务器的同意消息
        agree = self.client_socket.recv(4)
        type = struct.unpack('!H', agree)[0]  # 解析同意消息的报文类型
        if type != 2:
            # 如果未接收到同意消息，断开与服务器的连接
            print("未接收到同意消息，与服务器断开连接")
            self.client_socket.close()  # 关闭客户端连接
            return

        temp_data = []  # 初始化临时数据列表，用于存储反转后的数据块
        for i, block in enumerate(blocks):
            # 发送反转请求报文，包含报文类型和块长度
            # 报文类型3表示反转请求报文，块长度表示当前数据块的长度
            reverseRequest = struct.pack("!HI", 3, len(block)) + block.encode('utf-8')
            self.client_socket.sendall(reverseRequest)  # 发送反转请求报文到服务器

            # 接收反转后的数据报文
            packet = self.client_socket.recv(2)
            type = struct.unpack('!H', packet)[0]  # 解析服务器返回的报文类型

            if type == 4:
                # 接收到服务器发来的报文类型为4，表示服务器发回了反转的数据
                packet = self.client_socket.recv(4)
                # 从服务器接收数据长度字段（4字节）
                length = struct.unpack('!I', packet)[0]  # 解析反转数据的长度字段
                # 将收到的4字节数据解析为一个无符号整数，表示反转数据的长度
                reversed_block = b''
                # 初始化存储反转数据的字节串
                if length <= 1024:
                    # 如果数据长度小于等于1024字节，则一次性接收
                    reversed_block += self.client_socket.recv(length)  # 接收反转后的数据
                else:
                    # 如果数据长度大于1024字节，需要分块接收
                    has_recv_data = 0  # 初始化已接收数据长度
                    while True:
                        # 循环接收数据，每次最多接收1024字节
                        chunk = self.client_socket.recv(1024)  # 分块接收数据，每次接收1024字节
                        reversed_block += chunk  # 将接收到的数据块追加到反转数据中
                        has_recv_data += len(chunk)  # 更新已接收数据长度
                        if has_recv_data == length:
                            # 如果已接收数据长度等于预期长度，则退出循环
                            break
                # 将接收到的字节数据解码为UTF-8字符串
                reversed_block = reversed_block.decode('utf-8')  # 解码反转后的数据
                # 打印当前块的反转数据
                print(f"\n第{i + 1}块: {reversed_block}")
                # 将当前块的反转数据添加到临时数据列表中
                temp_data.append(reversed_block)

        reversed_data = temp_data[::-1]  # 反转接收到的所有数据块
        with open('reversed_file.txt', 'w') as file:
            file.write(''.join(reversed_data))  # 将反转后的数据写入文件

        self.client_socket.close()  # 关闭客户端连接

# 程序入口
if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("输入格式: reversetcpclient.py <服务器IP> <服务器端口> <文件路径> <最小块大小> <最大块大小>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    filepath = sys.argv[3]
    Lmin = int(sys.argv[4])
    Lmax = int(sys.argv[5])

    client = TCPClient(server_ip, server_port)  # 创建TCP客户端实例
    client.run(filepath, Lmin, Lmax)  # 运行客户端
