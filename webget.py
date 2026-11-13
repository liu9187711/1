import socket
import time

# 设置目标主机和端口
host = "www.bjfu.edu.cn"
port = 80

# 1. 创建 socket 并建立连接
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
print(f"正在连接 {host}...")
s.connect((host, port))

# 2. 构造 HTTP 请求
request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
s.sendall(request.encode('utf-8'))

# 3. 开始循环接收
data_buffer = b""     
recv_count = 0         
recv_sizes = []      
content_length = None  

print("开始接收数据...")

while True:
    try:
        chunk = s.recv(4096)
        
        if not chunk:
            print("\n[服务器关闭了连接]")
            break
            
        recv_count += 1
        recv_sizes.append(len(chunk))
        data_buffer += chunk

        if content_length is None and b"\r\n\r\n" in data_buffer:
            header_end_index = data_buffer.find(b"\r\n\r\n") + 4
            headers = data_buffer[:header_end_index].decode('utf-8', errors='ignore')

            for line in headers.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())
                    break
   
            if content_length is not None:
                current_body_len = len(data_buffer) - header_end_index
                print(f"[发现 Content-Length: {content_length}] 当前 Body 已收: {current_body_len}")
                if current_body_len >= content_length:
                    print("\n[已按 Content-Length 接收完毕]")
                    break
            else:
                pass

        elif content_length is not None:
            current_body_len = len(data_buffer) - header_end_index
            if current_body_len >= content_length:
                print("\n[已按 Content-Length 接收完毕]")
                break

    except socket.timeout:
        print("\n[错误：接收超时]")
        break
    except Exception as e:
        print(f"\n[发生错误: {e}]")
        break

s.close()

# 4. 验收打印
print("\n" + "="*40)
print(f"完整的响应内容（前 500 字节）:\n{data_buffer[:500].decode('utf-8', errors='ignore')}")
print("..." if len(data_buffer) > 500 else "")
print("="*40)
print(f"【统计信息】")
print(f"recv 总共调用了: {recv_count} 次")
print(f"每次接收的字节数: {recv_sizes}")
print(f"总共接收的字节数: {len(data_buffer)}")