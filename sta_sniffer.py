import os
import time
import sys
import json
import socket
from threading import Thread

# project local package
from ping import do_one as ping_one
from py_logger import py_log
import sta_sync_def
# for debugging use
import pdb

class STASniffer(Thread):
    """Sniffer of Wi-Fi Connected Clients"""

    def __init__(self, server_addr, dhcp_lease_file, check_client_period=5, sync_timeout=1):
        # init threading
        Thread.__init__(self)

        # dhcp client file 
        assert os.path.isfile(dhcp_lease_file), dhcp_lease_file + " is not a valid file!"
        self.dhcp_lease_file = dhcp_lease_file
        self.check_client_period = check_client_period
        self.sync_timeout = sync_timeout

        # socket to contact with main thread
        self.sync_ev_socket = None
        self.sync_ev_server = server_addr

        # thread running flag
        self.runnning_flag = False

        
    def check_client_state(self):
        # parse dhcp lease file to get connected client
        conn_sta_ev = []
        
        dhcp_fd = open(self.dhcp_lease_file, "r") 
        dhcp_list = dhcp_fd.readlines()
        dhcp_fd.close()

        for dhcp_line in dhcp_list:
            # read and parse sta info
            sta_sync_event = sta_sync_def.STASyncEvent()
            sta_sync_event.read_dhcp_line(dhcp_line)

            py_log.debug(("STA: [{}]-[{}]-[{}]-[{}]".format( \
                sta_sync_event.sta_name, sta_sync_event.mac_addr, \
                sta_sync_event.ip_addr, sta_sync_event.conn_ts)))
            
            # generate a icmp pkt to see if the sta is there
            delay_second = ping_one(sta_sync_event.ip_addr, self.sync_timeout)
            if delay_second:
                sta_sync_event.sync_delay = long(round(delay_second * 1000000))
                py_log.debug("Resp received from [{}]-[{}] delay = {} us".format( \
                        sta_sync_event.ip_addr, sta_sync_event.mac_addr, sta_sync_event.sync_delay))
                # generate json string 
                sta_sync_event_json = json.dumps(sta_sync_event.get_event_dict())
                if self.sync_ev_socket:
                    self.sync_ev_socket.sendto(sta_sync_event_json, self.sync_ev_server)
                
            else:
                py_log.warning("No resp received from [{}]-[{}]".format( \
                        sta_sync_event.ip_addr, sta_sync_event.mac_addr))
    
    def sync_socket_create(self):
        # delete socket file if it exists
        if not os.path.exists(self.sync_ev_server):
            py_log.error("UNIX UDP socket server address ({}) does not exist!".format(self.sync_ev_server))
            py_log.error("No socket created!")
            self.sync_ev_server = None
            self.sync_ev_socket = None
            return

        # create unix domain socket (udp based)
        self.sync_ev_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            

    # thread related function
    def sniff_start(self):
        self.runnning_flag = True
        self.daemon = True
        self.start()

    def sniff_stop(self):
        self.runnning_flag = False

    def run(self):
        self.sync_socket_create()
        if not self.sync_ev_socket:
            py_log.error("No socket available ==> thread exits")
            return

        while self.runnning_flag:
            self.check_client_state()    
            time.sleep(self.check_client_period)

        # close socket
        self.sync_ev_socket.close()


# ============================= main processing starts from here ================================

def main(argv):
    if len(argv) < 2:
        dhcp_lease_file = "dhcp.leases"
    else:
        dhcp_lease_file = argv[1]
    
    server_addr = './uds_socket'
    sta_sniffer = STASniffer(server_addr, dhcp_lease_file, check_client_period=5, sync_timeout=1)
    sta_sniffer.sniff_start()
#    sta_sniffer.sync_socket_create()
#    sta_sniffer.check_client_state()
    while True:
        py_log.info("I am main")
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv)
