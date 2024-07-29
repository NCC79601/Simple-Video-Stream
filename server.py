import cv2
import socket
import json5 as json
import time
import argparse

class Server(object):
    def __init__(self, server_ip: str, server_port: int, camera_id: int, frame_size: tuple, jpeg_quality: int):
        '''
        Initialize a Server object.

        Parameters:
        - server_ip: IP of the server, e.g. '127.0.0.1'
        - server_port: Port of the server, e.g. 8888
        - camera_id: ID of the camera to capture video, e.g. 0
        - frame_size: Size of the video frame, e.g. (1080, 720)
        - jpeg_quality: Quality of JPEG compression, e.g. 30
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_ip, self.server_port))
        self.server.listen(1)
        self.capture = cv2.VideoCapture(camera_id)
        self.frame_size = frame_size
        self.jpeg_quality = jpeg_quality

    def run(self):
        '''Run the server.'''
        try:  # connect to the client
            while True:
                print('Waiting for connection...')
                conn, addr = self.server.accept()
                print(f'Connected by {addr}')

                with conn:
                    try:  # send video frames to the client
                        while True:
                            # Capture video frame
                            ret, frame = self.capture.read()
                            if not ret:
                                print('Camera offline. Exiting...')
                                break

                            # Resize frame
                            frame = cv2.resize(frame, self.frame_size)
                            # Encode the video frame as JPEG
                            _, data = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
                            # Send the compressed video data
                            data_bytes = data.tobytes()
                            conn.sendall(len(data_bytes).to_bytes(4, 'big') + data_bytes)
                            print('Frame sent.')

                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

                    except socket.error as e:
                        if e.errno == 32:  # Broken pipe
                            print(f"Client disconnected abruptly: {e}")
                        else:
                            print(f"Socket error: {e}")
                    finally:
                        conn.close()
                        print('connection closed.')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.capture.release()
            self.server.close()
            print('Server shut down.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video Streaming Server')
    parser.add_argument('--config', type=str, default="config.json", help='Path to config file')
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)
        
    server = Server(
        server_ip=config['server_ip'], 
        server_port=config['server_port'], 
        camera_id=config['camera_id'],
        frame_size=tuple(config['frame_size']),
        jpeg_quality=config['jpeg_quality']
    )
    server.run()
