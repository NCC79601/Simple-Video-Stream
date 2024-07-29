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

        # Create a socket object
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the provided IP and port
        self.server.bind((self.server_ip, self.server_port))
        # Start listening for incoming connections, with a maximum queue of 1
        self.server.listen(1)

    def run(self):
        '''Run the server.'''
        print('Waiting for connection...')
        # Accept a connection
        conn, addr = self.server.accept()
        print(f'Connected by {addr}')

        with conn:
            try:
                while True:
                    # Receive the length of the incoming data (4 bytes)
                    length_bytes = conn.recv(4)
                    assert length_bytes, "Connection closed by the client."
                    length = int.from_bytes(length_bytes, 'big')

                    # Initialize a byte buffer to store the incoming data
                    data = b''
                    while len(data) < length:
                        remaining_bytes = length - len(data)
                        print(f'Remaining bytes to receive: {remaining_bytes}')
                        # Read in chunks of data, up to 4096 bytes
                        chunk_size = min(4096, remaining_bytes)
                        packet = conn.recv(chunk_size)
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
                    if cv2.waitKey(1) == ord('q'):
                        break

            except AssertionError as e:
                print(f'AssertionError: {e}')
            except Exception as e:
                print(f'Error: {e}')
            finally:
                # Close the connection
                conn.close()
                print('Connection closed.')

        # Close the server socket
        self.server.close()
        print('Server shut down.')
        # Destroy all OpenCV windows
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # Load configuration from a JSON file
    with open('config.json', 'r') as f:
        config = json.load(f)
    # Create a server object with the loaded configuration
    server = Server(server_ip=config['server_ip'], server_port=config['server_port'])
    # Run the server
    server.run()
