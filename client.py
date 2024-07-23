# for client
import cv2
import socket
import json
import numpy as np

class Client(object):
    def __init__(self, server_ip: str, server_port: int = 8888):
        '''
        Initialize a Client object.

        Parameters:
        - server_ip: ip of the server
        - server_port: port of the server, default: 8888
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.capture = cv2.VideoCapture(0)

    def run(self):
        '''Run the client.'''
        print(f'Connecting to server {self.server_ip}:{self.server_port}...')
        self.client.connect((self.server_ip, self.server_port))
        print('Connected to server.')
        while True:
            # 采集视频帧
            ret, frame = self.capture.read()
            if not ret:
                break
            
            # 缩小 frame
            frame = cv2.resize(frame, (800, 450))

            # 对视频帧进行编码压缩
            _, data = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            # 发送压缩后的视频数据
            print('Sending frame...')
            data_bytes = data.tobytes()
            self.client.sendall(len(data_bytes).to_bytes(4, 'big') + data_bytes)
            print('Frame sent.')
                    
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', "r") as f:
        config = json.load(f)
    client = Client(server_ip=config['server_ip'], server_port=config['server_port'])
    client.run()