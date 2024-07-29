from server import Server
from client import Client
import multiprocessing
import time
import json


def run_server():
    with open('config.json', 'r') as f:
        config = json.load(f)
    server = Server(hostname='127.0.0.1', port=config['port'])
    server.run()

def run_client():
    with open('config.json', "r") as f:
        config = json.load(f)
    client = Client(hostname='127.0.0.1', port=config['port'])
    client.run()

if __name__ == '__main__':
    server_thread = multiprocessing.Process(target=run_server)
    client_thread = multiprocessing.Process(target=run_client)

    server_thread.start()
    time.sleep(1)
    client_thread.start()

    print('Running test...')
    for _ in enumerate(range(10)):
        time.sleep(1)
    
    print('Test complete.')

    server_thread.terminate()
    client_thread.terminate()

    server_thread.join()
    client_thread.join()