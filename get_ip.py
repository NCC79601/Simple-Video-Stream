import socket

host = socket.gethostname() 
print(f'Host: {host}')

ip = socket.gethostbyname(host)
print(f'IP: {ip}')
