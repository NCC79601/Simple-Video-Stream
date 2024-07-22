# for client
import cv2
import socket
import json
import pickle
from image_chunk import make_transfer_blob_list
import PIL

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
            
            # resize the video frame
            frame = cv2.resize(frame, (1280, 720))
            frame = PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # make transfer blobs
            transfer_blobs = make_transfer_blob_list(frame, chunk_size=40)

            # print(f'transfer_blobs len: {len(transfer_blobs)}')
            
            for blob in transfer_blobs:
                data = pickle.dumps(blob)
                self.client.sendto(data, (self.server_ip, self.server_port))
                
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    with open('config.json', "r") as f:
        config = json.load(f)
    client = Client(server_ip=config['server_ip'], server_port=config['server_port'])
    client.run()