import socket
import sys
import time
import os
import asyncore
import async_timer
from py_logger import py_log
import pdb

##### read global config ####
from config_parser import global_config

dhcp_lease_file = global_config.dhcp_lease_file
arp_table_file = global_config.arp_table_file
check_client_period = global_config.check_client_period
sync_pkt_timeout = global_config.sync_pkt_timeout
sync_ev_server_addr = global_config.sync_ev_server_addr
sync_session_check_period = global_config.sync_session_check_period

##### init sta sync socket #####
from central_controller import STASyncServer
# Make sure the socket does not already exist
try:
    os.unlink(sync_ev_server_addr)
except OSError:
    if os.path.exists(sync_ev_server_addr):
        raise
# Create an event poll with UNIX domain socket
sta_sync_server = STASyncServer(sync_ev_server_addr)
if sta_sync_server.socket == None:
    py_log.error("Failed to create sta sync server ==> exit with -1")
    sys.exit(-1)

# Timer to check session expiration
sta_ss_timer_queue = async_timer.AsyncTimerQueue("sta_session_check")
sta_ss_timer_event = async_timer.AsyncTimerEvent(sync_session_check_period, True, sta_sync_server.process_outdated_sessions)
sta_ss_timer_queue.timer_put(sta_ss_timer_event)

##### init sta_sniffer thread #####
from sta_sniffer import STASniffer
sta_sync_sniffer = STASniffer(sync_ev_server_addr, dhcp_lease_file, arp_table_file, \
        check_client_period, sync_pkt_timeout)
sta_sync_sniffer.sniff_start()

##### start event poll #####
while True:
    # check socket (sync event from sta_sniffer)
    asyncore.loop(timeout=1, count=100)
    # check timer (sync session expiration)
    sta_ss_timer_queue.timer_batch_process()
    time.sleep(0.1)
