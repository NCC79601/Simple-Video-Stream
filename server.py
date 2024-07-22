# for servers
import cv2
import socket
import numpy as np
import json
from image_chunk import ImagePool
import pickle

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

        self.image_pool = ImagePool()

    def run(self):
        '''Run the server.'''
        while True:
            # Receive data from the client
            data, addr = self.server.recvfrom(65535) # 65535 bytes of data maximum
            transfer_blob = pickle.loads(data)

            print(f'Received transfer blob: timestamp = {transfer_blob["timestamp"]}, chunk_id = {transfer_blob["chunk_id"]}')

            # Handle the received data
            self.image_pool.add_transfer_blob(transfer_blob)

            if self.image_pool.has_new_image_received():
                print('New image received.')
                image = self.image_pool.received_image_pool.pop(0)['image']
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                cv2.imshow('frame', image)

            if cv2.waitKey(1) == ord('q'):
                break
        
        self.server.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    def recv_data_hander(data):
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('frame', frame)
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    server = Server(server_ip='127.0.0.1', server_port=config['server_port'])
    server.run(recv_data_hander=recv_data_hander)