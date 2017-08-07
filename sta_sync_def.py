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

    def get_event_dict(self):
        event_dict = {}
        event_dict['sta_name']      = self.sta_name
        event_dict['mac_addr']      = self.mac_addr
        event_dict['ip_addr']       = self.ip_addr
        event_dict['conn_ts']       = self.conn_ts
        event_dict['sync_delay']    = self.sync_delay
        return event_dict
