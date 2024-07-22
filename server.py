# 服务端
import cv2
import socket
import numpy as np
import json

with open('config.json', 'r') as f:
    config = json.load(f)

server_ip   = config['server_ip']
server_port = config['server_port']

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('127.0.0.1', server_port))
while True:
    # 接收客户端发送的数据
    data, addr = server.recvfromx(65535) # 一次最多接收 65535 个字节的数据
    # 解码压缩后的视频数据
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    # 显示解码后的视频数据
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
server.close()
cv2.destroyAllWindows()