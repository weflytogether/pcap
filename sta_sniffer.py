# system package
import os
import time
import sys
import socket
from threading import Thread
# project local package
from ping import do_one as ping_one
from py_logger import py_log
from config_parser import global_config
import sta_sync_def

class STASniffer(Thread):
    """Sniffer of Wi-Fi Connected Clients"""

    def __init__(self, server_addr, dhcp_lease_file, check_client_period=15, sync_pkt_timeout=1):
        # init threading
        Thread.__init__(self)

        # dhcp client file 
        self.dhcp_lease_file = dhcp_lease_file
        self.check_client_period = check_client_period
        self.sync_pkt_timeout = sync_pkt_timeout

        # socket to contact with main thread
        self.sync_ev_socket = None
        self.sync_ev_server = server_addr

        # thread running flag
        self.runnning_flag = False

        
    def check_client_state(self):
        # parse dhcp lease file to get connected client
        conn_sta_ev = []

        if not os.path.isfile(self.dhcp_lease_file):
            py_log.warning("DHCP lease file ({}) not exists ==> no connected clients".format(self.dhcp_lease_file))
            return
        
        dhcp_fd = open(self.dhcp_lease_file, "r") 
        dhcp_list = dhcp_fd.readlines()
        dhcp_fd.close()

        for dhcp_line in dhcp_list:
            # read and parse sta info
            sta_sync_event = sta_sync_def.STASyncEvent()
            sta_sync_event.read_dhcp_line(dhcp_line)

            py_log.debug(("DHCP STA: [{}]-[{}]-[{}]-[{}]".format( \
                sta_sync_event.sta_name, sta_sync_event.mac_addr, \
                sta_sync_event.ip_addr, sta_sync_event.conn_ts)))
            
            # generate a icmp pkt to see if the sta is there
            delay_second = ping_one(sta_sync_event.ip_addr, self.sync_pkt_timeout)
            if delay_second:
                sta_sync_event.sync_delay = long(round(delay_second * 1000000))
                py_log.debug("Sync resp received from [{}]-[{}] delay = {} us".format( \
                        sta_sync_event.ip_addr, sta_sync_event.mac_addr, sta_sync_event.sync_delay))
            else:
                py_log.warning("No sync resp received from [{}]-[{}]".format( \
                        sta_sync_event.ip_addr, sta_sync_event.mac_addr))

            # generate json string 
            sta_sync_event_json = sta_sync_event.get_event_json()
            if self.sync_ev_socket:
                self.sync_ev_socket.sendto(sta_sync_event_json, self.sync_ev_server)
    
    def sync_socket_create(self):
        # delete socket file if it exists
        if not os.path.exists(self.sync_ev_server):
            py_log.error("UNIX UDP socket server address ({}) does not exist!".format(self.sync_ev_server))
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

        py_log.info("STASniffer enters thread loop")
        while self.runnning_flag:
            self.check_client_state()    
            time.sleep(self.check_client_period)
        py_log.info("STASniffer exits thread")

        # close socket
        self.sync_ev_socket.close()


# ============================= for testing ================================
if __name__ == '__main__':
    server_addr = global_config.sync_ev_server_addr
    dhcp_lease_file = global_config.dhcp_lease_file
    check_client_period = global_config.check_client_period
    sync_pkt_timeout = global_config.sync_pkt_timeout

    sta_sniffer = STASniffer(server_addr, dhcp_lease_file, check_client_period, sync_pkt_timeout)
    if hasattr(sta_sniffer, 'dhcp_lease_file'):
        sta_sniffer.sniff_start()
    else:
        sys.exit(-1)

    while True:
        py_log.info("I am main thread")
        time.sleep(10)
