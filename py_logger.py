import logging

global_log_level = logging.DEBUG
class PyLogger:
    def __init__(self):
        self.logger = logging.getLogger('root')
        FORMAT = "[%(filename)s:%(lineno)s-%(funcName)s()|%(levelname)s] %(message)s"
        logging.basicConfig(format=FORMAT)
        self.logger.setLevel(global_log_level)

py_log = PyLogger().logger
