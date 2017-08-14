import os

class ConfigParser():

    def __init__(self, config_file):
        assert os.path.isfile(config_file), "Not a valid config file!"
        self.config_file = config_file
        # supported configs
        self.dhcp_lease_file = None
        self.arp_table_file = None
        self.check_client_period = 15
        self.sync_pkt_timeout = 1

        self.sync_ev_server_addr = None
        self.sync_delay_list_max = 100
        self.sync_session_expire = 60
        self.sync_session_check_period = 15
        self.parse_config()
        
    def parse_config(self):
        config_fd = open(self.config_file, "r") 
        config_lines = config_fd.readlines()
        config_fd.close()

        config = {}
        for cf in config_lines:
            if cf[0] == '#':
                continue
            if '=' not in cf:
                continue

            cf_parsed = cf.split('=')
            # parse all possible config
            if cf_parsed[0] == "dhcp_lease_file":
                self.dhcp_lease_file = (cf_parsed[1].split())[0]
            elif cf_parsed[0] == "arp_table_file":
                self.arp_table_file = (cf_parsed[1].split())[0]
            elif cf_parsed[0] == "check_client_period":
                self.check_client_period = int((cf_parsed[1].split())[0])
            elif cf_parsed[0] == "sync_pkt_timeout":
                self.sync_pkt_timeout = int((cf_parsed[1].split())[0])
            elif cf_parsed[0] == "sync_ev_server_addr":
                self.sync_ev_server_addr = (cf_parsed[1].split())[0]
            elif cf_parsed[0] == "sync_delay_list_max":
                self.sync_delay_list_max = int((cf_parsed[1].split())[0])
            elif cf_parsed[0] == "sync_session_expire":
                self.sync_session_expire = int((cf_parsed[1].split())[0])
            elif cf_parsed[0] == "sync_session_check_period":
                self.sync_session_check_period = int((cf_parsed[1].split())[0])

global_config = ConfigParser('sniffer.config')
