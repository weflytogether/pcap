import time
import asyncore
import socket
import sta_sync_def 
from py_logger import py_log
from config_parser import global_config

class STASyncServer(asyncore.dispatcher):

    def __init__(self, sync_ev_server_addr=('localhost', 0)):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.bind(sync_ev_server_addr)
        py_log.info("Sta sync server starting up on {}".format(sync_ev_server_addr))

        self.sta_sync_sessions = {}         # dict {MAC:Session}
        self.sync_delay_list_max = global_config.sync_delay_list_max

    def handle_read(self):
        sync_ev_json = self.recv(4096)
        
        # read sync event
        sync_ev = sta_sync_def.STASyncEvent()       
        sync_ev.read_ev_json(sync_ev_json)
        # debug use
        py_log.debug("Received event: {}".format(sync_ev.get_event_json()))

        self.update_sync_session(sync_ev)

    def update_sync_session(self, sync_ev):
        if not isinstance(sync_ev, sta_sync_def.STASyncEvent):
            raise
        if sync_ev.mac_addr in self.sta_sync_sessions:
            sync_session = self.sta_sync_sessions[sync_ev.mac_addr]
            if sync_ev.sync_delay == -1:
                # sta no response
                self.finalize_sync_session(sync_ev.mac_addr)        
            elif sync_ev.conn_ts != sync_session.conn_ts:
                # different connection timestamp ==> start a new session
                self.finalize_sync_session(sync_ev.mac_addr)
                sync_session = sta_sync_def.STASyncSession()
                sync_session.init_ev(sync_ev)
                self.sta_sync_sessions[sync_ev.mac_addr] = sync_session
            else:
                # if sync_delay_list reach a maximum ==> start a new session
                # otherwise, update event to the session
                if len(sync_session.sync_delay_list) == self.sync_delay_list_max:
                    self.finalize_sync_session(sync_ev.mac_addr)
                    sync_session = sta_sync_def.STASyncSession()
                    sync_session.init_ev(sync_ev)
                    self.sta_sync_sessions[sync_ev.mac_addr] = sync_session
                else:
                    sync_session.update_ev(sync_ev)
        else:
            if sync_ev.sync_delay == -1:
                py_log.warning("Invalid sync event ({}) with sync_delay {} ==> ev dropped".format(\
                        sync_ev.mac_addr, sync_ev.sync_delay))
                return
            # start a new session
            sync_session = sta_sync_def.STASyncSession()
            sync_session.init_ev(sync_ev)
            self.sta_sync_sessions[sync_ev.mac_addr] = sync_session
        
    def finalize_sync_session(self, mac_addr):
        # fill end timestamp
        sync_session = self.sta_sync_sessions[mac_addr]
        sync_session.end_ts = int(time.time())
        # TODO: report to cloud
        sync_session_json = sync_session.get_session_json()
        py_log.debug("Sync session finalized: {}".format(sync_session_json))
        # remove session
        del self.sta_sync_sessions[mac_addr]