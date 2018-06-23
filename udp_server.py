import socket
import json
import pdb
UDP_IP = "10.0.1.4"
UDP_PORT = 55555

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
except:
    raise

while True:
    data, addr = sock.recvfrom(4096) # buffer size is 1024 bytes
    data_json = json.loads(data)
    print "received message from", addr
    print "STA {} MAC {} - sync_delay {} sync_ts {}".format(\
            data_json['sta_name'], data_json['mac_addr'],  \
            data_json['sync_delay_list'], data_json['sync_ts_list'])
    print ""
