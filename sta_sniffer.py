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

    def __init__(self, server_addr, dhcp_lease_file, arp_table_file, \
            check_client_period=15, sync_pkt_timeout=1):
        # init threading
        Thread.__init__(self)

        # dhcp client file 
        self.dhcp_lease_file = dhcp_lease_file
        self.arp_table_file = arp_table_file
        self.check_client_period = check_client_period
        self.sync_pkt_timeout = sync_pkt_timeout

        # socket to contact with main thread
        self.sync_ev_server = server_addr
        self.sync_ev_socket = None

        # thread running flag
        self.runnning_flag = False

        
    def check_client_state(self):
        # parse dhcp lease file to get connected client
        conn_sta_ev = []

        if not os.path.isfile(self.dhcp_lease_file):
            py_log.warning("DHCP lease file ({}) not exists ==> no connected clients".format(self.dhcp_lease_file))
            return

        # read arp table (only read br-lan interface)
        arp_fd = open(self.arp_table_file, "r")
        arp_list = arp_fd.readlines()
        arp_fd.close()
        arp_flags = {}     
        for arp_line in arp_list:
            if arp_line.find("br-lan") != -1:
                arp_line_items = arp_line.split()
                arp_flags[arp_line_items[3]] = int(arp_line_items[2], 16)

        # read DHCP lease
        dhcp_fd = open(self.dhcp_lease_file, "r") 
        dhcp_list = dhcp_fd.readlines()
        dhcp_fd.close()

        for dhcp_line in dhcp_list:
            # read and parse sta info
            sta_sync_event = sta_sync_def.STASyncEvent()
            # basic dhcp info
            sta_sync_event.read_dhcp_line(dhcp_line)
            # arp info
            if sta_sync_event.mac_addr in arp_flags.keys():
                sta_sync_event.arp_conn = False if arp_flags[sta_sync_event.mac_addr] == 0 else True
            # sync timestamp
            sta_sync_event.sync_ts = int(round(time.time()))

            py_log.debug(("STA DHCP: [NAME {}]-[MAC {}]-[IP {}]-[ARP {}]".format( \
                sta_sync_event.sta_name, sta_sync_event.mac_addr, \
                sta_sync_event.ip_addr, sta_sync_event.arp_conn)))

            # read arp connection status
            sta_sync_event.sync_delay = -1
            if sta_sync_event.arp_conn == True:
                # generate a icmp pkt to see if the sta is there
                delay_second = ping_one(sta_sync_event.ip_addr, self.sync_pkt_timeout)
                if delay_second:
                    sta_sync_event.sync_delay = long(round(delay_second * 1000000))
                    py_log.info("STA: Sync resp received from [{}]-[{}] delay = {} us".format( \
                            sta_sync_event.ip_addr, sta_sync_event.mac_addr, sta_sync_event.sync_delay))
                else:
                    py_log.warning("STA: No sync resp received from [{}]-[{}]".format( \
                            sta_sync_event.ip_addr, sta_sync_event.mac_addr))
            else:
                py_log.info("STA ARP: [{}] not connected ==> sync_delay = -1".format(sta_sync_event.mac_addr))

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
    dhcp_lease_file = global_config.dhcp_lease_file
    arp_table_file = global_config.arp_table_file
    check_client_period = global_config.check_client_period
    sync_pkt_timeout = global_config.sync_pkt_timeout
    server_addr = global_config.sync_ev_server_addr

    sta_sniffer = STASniffer(server_addr, dhcp_lease_file, arp_table_file, \
            check_client_period, sync_pkt_timeout)
    sta_sniffer.sniff_start()

    while True:
        py_log.debug("I am main thread")
        time.sleep(10)
