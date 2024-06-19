import socket
import struct
import select

# TCP服务器类
class TCPServer:
    # 初始化服务器，绑定IP和端口，配置服务器套接字
    def __init__(self, ip, port):
        self.block_cnt = 0  # 用于存储接收到的块计数
        self.server_ip = ip  # 服务器IP地址
        self.server_port = port  # 服务器端口
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字
        self.server_socket.setblocking(False)  # 设置非阻塞模式
        self.server_socket.bind((self.server_ip, self.server_port))  # 绑定IP和端口
        self.server_socket.listen(50)  # 监听连接，最大连接数为50
        print(f"服务器在 {self.server_ip}:{self.server_port} 监听中")  # 输出服务器启动信息

    # 运行服务器
    def run(self):
        inputs = [self.server_socket, ]  # 初始化监听列表，包括服务器套接字
        while True:
            # 使用select监听套接字，超时设置为0.05秒
            r, _, _ = select.select(inputs, [], [], 0.05)
            for sock in r:
                if sock == self.server_socket:
                    # 接受新的客户端连接
                    client_socket, addr = self.server_socket.accept()
                    print(f"\n接受来自 {addr} 的连接")
                    inputs.append(client_socket)  # 将新连接加入监听列表
                else:
                    # 接收客户端的报文类型字段
                    packet = sock.recv(2)
                    addr = sock.getpeername()  # 获取客户端地址
                    if not packet:
                        # 如果接收不到数据，说明客户端断开连接
                        print(f'\n客户端{addr}断开连接')
                        sock.close()  # 关闭套接字
                        inputs.remove(sock)  # 从监听列表中移除
                    else:
                        print(f'\n从客户端{addr}收到报文Type字段：packet={packet}')
                        type = struct.unpack('!H', packet)[0]  # 解析报文类型字段
                        print(f"报文解析：type={type}")
                        if type == 1:
                            # 处理类型为1的报文，接收块计数字段
                            packet = sock.recv(4)
                            print(f'从客户端{addr}收到报文block_cnt字段：packet={packet}')
                            self.block_cnt = struct.unpack('!I', packet)[0]  # 解析块计数字段
                            print(f"报文解析：block_cnt={self.block_cnt}")
                            agree = struct.pack('!H', 2)  # 构建同意报文
                            sock.sendall(agree)  # 发送同意报文
                            print(f'发送agree报文：agree={agree}')
                        elif type == 3:
                            # 处理类型为3的报文，接收数据长度字段
                            packet = sock.recv(4)
                            print(f'从客户端{addr}收到报文length字段：packet={packet}')
                            length = struct.unpack('!I', packet)[0]  # 解析数据长度字段
                            print(f"报文解析：length={length}")
                            data = b''
                            if length <= 1024:
                                data += sock.recv(length)  # 接收数据
                            else:
                                # 如果数据长度超过1024字节，分块接收数据
                                has_recv_data = 0
                                while True:
                                    chunk = sock.recv(1024)
                                    data += chunk
                                    has_recv_data += len(chunk)
                                    if has_recv_data == length:
                                        break
                            data = data.decode('utf-8')  # 解码数据
                            print(f'\n从客户端{addr}收到数据:\n{data}')
                            data_reversed = data[::-1]  # 反转数据
                            print(f'反转数据：\n{data_reversed}')
                            reverseAnswer = struct.pack('!HI', 4, len(data_reversed)) + data_reversed.encode('utf-8')  # 构建反转数据报文
                            sock.sendall(reverseAnswer)  # 发送反转数据报文

# 程序入口
if __name__ == "__main__":
    server = TCPServer("127.0.0.1", 9999)  # 创建TCP服务器实例
    server.run()  # 运行服务器
