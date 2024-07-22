# for client
import cv2
import socket
import json

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

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.capture = cv2.VideoCapture(0)

    def run(self):
        '''Run the client.'''
        while True:
            # Capture video frame
            ret, frame = self.capture.read()
            if not ret:
                break
            # Resize the video frame to 480p
            frame = cv2.resize(frame, (160, 120))
            # Encode and compress the video frame
            _, data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            print(f'Frame shape: {frame.shape}')
            print(f'Data size: {len(data.tobytes())}')
            # Send the compressed video data
            self.client.sendto(data.tobytes(), (self.server_ip, self.server_port))

        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', "r") as f:
        config = json.load(f)
    client = Client(server_ip=config['server_ip'], server_port=config['server_port'])
    client.run()