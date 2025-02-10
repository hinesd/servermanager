from pathlib import Path

from mcrcon import MCRcon

from config import ENV_NAME
import mcrcon

class ServerManager:

    def __init__(self):
        ## Server Attributes
        self.process_manager = None
        self.base_path = next(p for p in Path(__file__).resolve().parents if p.name == 'server_controller')
        self.server_path = f'{self.base_path}/server' if ENV_NAME == 'prod' else f'{self.base_path}/testserver'
        self.server_connection: MCRcon | None = None
        self.server_properties = self._init_server_properties()

    def _init_server_properties(self):
        # TODO
        #  add logic to dynamically override server.properties using attributes defined in config.py before load
        #  add logic to dynamically load start_script configs into settings.sh defined in config.py before load
        return dict([x.split('=') for x in open(self.server_path + 'server.properties').read().strip().split('\n')[2:]])