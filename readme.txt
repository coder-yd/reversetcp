TCP Socket 编程项目
1. 概述
	本项目展示了一个使用自定义应用层报文结构的TCP客户端-服务器应用的实现。客户端读取一个ASCII文件，发送不定长的文本块给服务器，服务器将文本反转后返回给客户端。客户端打印反转后的文本，最终输出整个反转后的文件。

2. 目的
	理解并掌握TCP socket程序设计的基本结构及工作过程。
	掌握构造应用层自定义的报文结构及报文交互。

3. 报文结构
	客户端和服务器之间共四种类型报文：
	Initialization 报文 (类型1): Type(2 Bytes) N(4 Bytes)，N表示要请求服务器反转的块数。
	Agree 报文 (类型2): Type(2 Bytes)。
	ReverseRequest 报文 (类型3): Type(2 Bytes) Length(4 Bytes) Data，Data是待反转的数据。
	ReverseAnswer 报文 (类型4): Type(2 Bytes) Length(4 Bytes) Data，Data是反转后的数据。

4. 运行环境
	Python 3.x
	需要的库：socket、random、sys、struct、select

5. 配置选项
	在运行客户端时，需要在命令行中指定以下参数：

	服务器IP地址
	服务器端口号
	文件路径
	最小块大小（Lmin）
	最大块大小（Lmax）

6. 使用说明

6.1 运行服务器
	服务器运行在guest OS，使用以下命令启动服务器：
	
	python3 server.py

6.2 运行客户端
	客户端运行在host OS，使用以下命令启动客户端：

	python3 client.py <服务器IP> <服务器端口> <文件路径> <最小块大小> <最大块大小>
例如：

	python3 client.py 127.0.0.1 9999 ascii_file.txt 50 520

6.3 客户端和服务器的交互流程
	客户端读取指定的ASCII文件，并将其分成不定长的块，每块大小在Lmin和Lmax之间。
	客户端向服务器发送Initialization报文，告知服务器块的数量。
	服务器接收Initialization报文并回复Agree报文。
	客户端逐块发送ReverseRequest报文，每个报文包含块的长度和数据。
	服务器接收ReverseRequest报文，反转数据后发送ReverseAnswer报文。
	客户端接收ReverseAnswer报文，打印反转后的文本块，最终输出整个反转后的文件。