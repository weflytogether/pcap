import json
from py_logger import py_log


class STASyncEvent():

    def __init__(self):
        self.sta_name   = "STA_Default"         # default station name
        self.mac_addr   = "00:00:00:00:00:00"   # null mac address
        self.ip_addr    = "192.168.0.1"         # default ip address
        self.conn_ts    = 0L                    # connection starting timestamp (second)
        self.sync_delay = -1L                   # sync delay (micro-second)
        
    def read_dhcp_line(self, dhcp_line):
        dhcp_entry = dhcp_line.split()
        if len(dhcp_entry) <= 4:
            py_log.error("Corrupted DHCP line: \"{}\"".format(dhcp_line))
            py_lod.error("No valid info is initialized!")
            return
        # init sync event
        self.conn_ts    = long(dhcp_entry[0])
        self.mac_addr   = dhcp_entry[1]
        self.ip_addr    = dhcp_entry[2]
        self.sta_name   = dhcp_entry[3]

    def read_ev_json(self, sta_ev_json):
        event_dict = json.loads(sta_ev_json)
        self.sta_name   = event_dict['sta_name']
        self.mac_addr   = event_dict['mac_addr']
        self.ip_addr    = event_dict['ip_addr']
        self.conn_ts    = event_dict['conn_ts']
        self.sync_delay = event_dict['sync_delay']

    def get_event_dict(self):
        event_dict = {}
        event_dict['sta_name']      = self.sta_name
        event_dict['mac_addr']      = self.mac_addr
        event_dict['ip_addr']       = self.ip_addr
        event_dict['conn_ts']       = self.conn_ts
        event_dict['sync_delay']    = self.sync_delay
        return event_dict

    def get_event_json(self):
        ev_json = json.dumps(self.get_event_dict())
        return ev_json

    def print_sync_event(self):
        py_log.debug("sta_name: {}".format(self.sta_name))
        py_log.debug("mac_addr: {}".format(self.mac_addr))
        py_log.debug("ip_addr: {}".format(self.ip_addr))
        py_log.debug("conn_ts: {}".format(self.conn_ts))
        py_log.debug("sync_delay: {}".format(self.sync_delay))



class STASyncSession():

    def __init__(self):
        self.sta_name   = "STA_Default"         # default station name
        self.mac_addr   = "00:00:00:00:00:00"   # null mac address
        self.ip_addr    = "192.168.0.1"         # default ip address
        self.conn_ts    = 0L                    # connection starting timestamp (second)
        self.end_ts     = 0L                    # connection starting timestamp (second)
        self.sync_delay_list = []               # sync delay list (micro-second)
        
    def init_ev(self, sta_sync_event):
        if not isinstance(sta_sync_event, STASyncEvent):
            raise
        py_log.debug("init sync event session for {}-{}".format( \
                sta_sync_event.sta_name, sta_sync_event.mac_addr))
        self.sta_name   = sta_sync_event.sta_name
        self.mac_addr   = sta_sync_event.mac_addr
        self.ip_addr    = sta_sync_event.ip_addr
        self.conn_ts    = sta_sync_event.conn_ts
        self.end_ts     = -1
        self.sync_delay_list = [sta_sync_event.sync_delay]

    def update_ev(self, sta_sync_event):
        if not isinstance(sta_sync_event, STASyncEvent):
            raise
        py_log.debug("update sync event session for {}-{}".format( \
                sta_sync_event.sta_name, sta_sync_event.mac_addr))
        if sta_sync_event.mac_addr == self.mac_addr:
            self.sync_delay_list.append(sta_sync_event.sync_delay)
        else:
            py_log.error("mismatched mac address -- sync event {} session {}".format( \
                    sta_sync_event.mac_addr, self.mac_addr))

    def get_session_dict(self):
        session_dict = {}
        session_dict['sta_name']      = self.sta_name
        session_dict['mac_addr']      = self.mac_addr
        session_dict['ip_addr']       = self.ip_addr
        session_dict['conn_ts']       = self.conn_ts
        session_dict['end_ts']        = self.end_ts
        session_dict['sync_delay_list'] = self.sync_delay_list
        return session_dict

    def get_session_json(self):
        session_json = json.dumps(self.get_session_dict())
        return session_json
