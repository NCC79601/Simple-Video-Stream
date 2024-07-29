import cv2
import socket
import json
import numpy as np
import time
import argparse

class Client(object):
    def __init__(self, server_ip: str, server_port: int, camera_id: int, frame_size: tuple, jpeg_quality: int):
        '''
        Initialize a Client object.

        Parameters:
        - server_ip: IP of the server, e.g. '127.0.0.1'
        - server_port: Port of the server, e.g. 8888
        - camera_id: ID of the camera to capture video, e.g. 0
        - frame_size: Size of the video frame, e.g. (1080, 720)
        - jpeg_quality: Quality of JPEG compression, e.g. 30
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.capture = cv2.VideoCapture(camera_id)
        self.frame_size = frame_size
        self.jpeg_quality = jpeg_quality

    def run(self):
        '''Run the client.'''
        try:
            print(f'Connecting to server {self.server_ip}:{self.server_port}...')
            self.client.connect((self.server_ip, self.server_port))
            print('Connected to server.')
            time.sleep(1)

            prev_time = time.time()
            frame_count = 0

            while True:
                # Capture video frame
                ret, frame = self.capture.read()
                if not ret:
                    print('Camera offline. Exiting...')
                    break

                # Resize frame
                frame = cv2.resize(frame, self.frame_size)
                cv2.imshow('Video Capture', frame)

                # Encode the video frame as JPEG
                _, data = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
                # Send the compressed video data
                data_bytes = data.tobytes()
                self.client.sendall(len(data_bytes).to_bytes(4, 'big') + data_bytes)

                # Calculate and print FPS
                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - prev_time

                if elapsed_time >= 1.0:
                    fps = frame_count / elapsed_time
                    print(f'FPS: {fps:.2f}')
                    prev_time = current_time
                    frame_count = 0

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.capture.release()
            cv2.destroyAllWindows()
            self.client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video Streaming Client')
    parser.add_argument('--config', type=str, default="config.json", help='Path to config file')
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)
        
    client = Client(
        server_ip=config['server_ip'], 
        server_port=config['server_port'], 
        camera_id=config['camera_id'],
        frame_size=tuple(config['frame_size']),
        jpeg_quality=config['jpeg_quality']
    )
    client.run()
