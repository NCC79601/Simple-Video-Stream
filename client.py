import cv2
import socket
import numpy as np
import json5 as json
import argparse

class Client(object):
    def __init__(self, server_ip: str, server_port: int):
        '''
        Initialize a Client object.

        Parameters:
        - server_ip: IP of the server, e.g. '127.0.0.1'
        - server_port: Port of the server, e.g. 8888
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        '''Run the client.'''
        try:
            print(f'Connecting to server {self.server_ip}:{self.server_port}...')
            self.client.connect((self.server_ip, self.server_port))
            print('Connected to server.')

            while True:
                # Receive the length of the incoming data (4 bytes)
                length_bytes = self.client.recv(4)
                assert length_bytes, "Connection closed by the server."
                length = int.from_bytes(length_bytes, 'big')

                # Initialize a byte buffer to store the incoming data
                data = b''
                while len(data) < length:
                    remaining_bytes = length - len(data)
                    print(f'Remaining bytes to receive: {remaining_bytes}')
                    # Read in chunks of data, up to 4096 bytes
                    chunk_size = min(4096, remaining_bytes)
                    packet = self.client.recv(chunk_size)
                    if not packet:
                        break
                    data += packet

                if len(data) != length:
                    print("Warning: Received data length does not match expected length.")
                    continue

                print('Frame received.')

                # Decode the received bytes into an image
                frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    print('Failed to decode frame.')
                    continue

                # Display the frame
                cv2.imshow('frame', frame)

                # Exit if 'q' key is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except AssertionError as e:
            print(f'AssertionError: {e}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.client.close()
            cv2.destroyAllWindows()
            print('Client shut down.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video Streaming Client')
    parser.add_argument('--config', type=str, default="config.json", help='Path to config file')
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)
        
    client = Client(
        server_ip=config['server_ip'], 
        server_port=config['server_port']
    )
    client.run()
