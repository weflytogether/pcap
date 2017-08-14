import socket
UDP_IP = "127.0.0.1"
UDP_PORT = 55555

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
except:
    raise

while True:
    data, addr = sock.recvfrom(4096) # buffer size is 1024 bytes
    print "received message:", data
