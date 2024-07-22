# 客户端
import cv2
import socket
import json

with open('config.json', "r") as f:
    config = json.load(f)

server_ip   = config["server_ip"]
server_port = config["server_port"]

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
capture = cv2.VideoCapture(0)
while True:
    # 采集视频帧
    ret, frame = capture.read()
    if not ret:
        break
    # 对视频帧进行编码压缩
    _, data = cv2.imencode('.jpg', frame)
    # 发送压缩后的视频数据
    client.sendto(data.tobytes(), (server_ip, server_port))

capture.release()
cv2.destroyAllWindows()