import socket
from py_logger import py_log

class CloudReporter():

    def __init__(self, cloud_server_ip='127.0.0.1', cloud_server_port=55555):
        
        self.cloud_server_ip = cloud_server_ip
        self.cloud_server_port = cloud_server_port

        # create udp based socket
        try:
            self.cloud_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            self.cloud_server_ip = None
            self.cloud_server_port = None
            self.cloud_socket = None

    def report_json_string(self, json_string):
        if not self.cloud_socket:
            py_log.error("No available socket ==> stop reporting!")
        else:
            py_log.debug("Report JSON ({}) reported to ({}, {})".format(json_string, \
                    self.cloud_server_ip, self.cloud_server_port))
            self.cloud_socket.sendto(json_string, (self.cloud_server_ip, self.cloud_server_port))
        
        

