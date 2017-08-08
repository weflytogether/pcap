import os

class ConfigParser():

    def __init__(self, config_file):
        assert os.path.isfile(config_file), "Not a valid config file!"
        self.config_file = config_file
        # supported configs
        self.sync_ev_server = None
        self.dhcp_lease_file = None
        self.parse_config()
        
    def parse_config(self):
        config_fd = open(self.config_file, "r") 
        config_lines = config_fd.readlines()
        config_fd.close()

        config = {}
        for cf in config_lines:
            cf_parsed = cf.split('=')
            # parse all possible config
            if cf_parsed[0] == "sync_ev_server":
                self.sync_ev_server = (cf_parsed[1].split())[0]
            elif cf_parsed[0] == "dhcp_lease_file":
                self.dhcp_lease_file = (cf_parsed[1].split())[0]
            elif cf_parsed[0] == "check_client_period":
                self.check_client_period = int((cf_parsed[1].split())[0])
            elif cf_parsed[0] == "sync_pkt_timeout":
                self.sync_pkt_timeout = int((cf_parsed[1].split())[0])

global_config = ConfigParser('sniffer.config')
