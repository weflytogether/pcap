import socket
import sys
import os
from config_parser import global_config

sync_ev_server = global_config.sync_ev_server

# Make sure the socket does not already exist
try:
    os.unlink(sync_ev_server)
except OSError:
    if os.path.exists(sync_ev_server):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)


# Bind the socket to the port
print >>sys.stderr, 'starting up on %s' % sync_ev_server
sock.bind(sync_ev_server)

while True:
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)
    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data
    
