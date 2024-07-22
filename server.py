# for servers
import cv2
import socket
import numpy as np
import json

class Server(object):
    def __init__(self, server_ip: str = '127.0.0.1', server_port: int = 8888):
        '''
        Initialize a Server object.

        Parameters:
        - server_ip: ip of the server, default: `127.0.0.1`
        - server_port: port of the server, default: 8888
        '''
        self.server_ip = server_ip
        self.server_port = server_port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.server_ip, self.server_port))

    def run(self):
        '''Run the server.'''
        while True:
            # Receive data from the client
            data, addr = self.server.recvfrom(65535) # 65535 bytes of data maximum
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break
        
        self.server.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)
    server = Server(server_ip='127.0.0.1', server_port=config['server_port'])
    server.run()