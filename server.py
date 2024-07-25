import cv2
import socket
import numpy as np
import json


class Server(object):
    def __init__(self, server_ip: str, server_port: int):
        '''
        Initialize a Server object.

        Parameters:
        - server_ip: ip of the server, e.g. `127.0.0.1`
        - server_port: port of the server, e.g. 8888
        '''
        self.server_ip = server_ip
        self.server_port = server_port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_ip, self.server_port))

        # listen(*) 操作系统为新连接请求保持排队的能力的限制
        self.server.listen(1)

    def run(self):
        '''Run the server.'''
        print('Waiting for connection...')
        conn, addr = self.server.accept()
        print('Connected by', addr)

        with conn:
            while True:
                length_bytes = conn.recv(4)
                if not length_bytes:
                    break
                length = int.from_bytes(length_bytes, 'big')
                data = b''
                while len(data) < length:
                    print(f' > remaining bytes to receive: {length - len(data)}')
                    # 确保每次读取的字节数是正数且不超过4096
                    chunk_size = min(4096 * 4, length - len(data))
                    packet = conn.recv(chunk_size)
                    if not packet:
                        break
                    data += packet

                print('Frame received.')

                if len(data) != length:
                    print("Warning: Received data length does not match expected length.")

                frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('frame', frame)

                if cv2.waitKey(1) == ord('q'):
                    break

        # 关闭服务器
        self.server.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    server = Server(server_ip=config['server_ip'], server_port=config['server_port'])
    server.run()
