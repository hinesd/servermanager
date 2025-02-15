from mcstatus import JavaServer
import asyncio
from core.process_manager import ProcessManager


class ServerManager:

    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager
        self.server_properties = self._init_server_properties()
        self.query_connection = JavaServer(process_manager.server_domain, int(self.server_properties['server-port']), timeout=30)

    def _init_server_properties(self):
        # TODO
        #  add logic to dynamically override server.properties using attributes defined in config.py before load
        #  add logic to dynamically load start_script configs into settings.sh defined in config.py before load
        return dict([x.split('=') for x in open(self.process_manager.server_path + '/server.properties').read().strip().split('\n')[2:]])

    async def init_server_connection(self):
        timeout = self.process_manager.timeout
        increment = 3
        while timeout > 0:
            try:
                return await self.query_connection.async_ping()
            except ConnectionRefusedError:
                await asyncio.sleep(increment)
                timeout -= increment
            except Exception as e:
                await self.process_manager.stop()
                raise e
        await self.process_manager.stop()
        raise ConnectionRefusedError()

    async def server_status(self, query=None):
        await self.process_manager.validate_process()
        results = (await self.query_connection.async_status()).__dict__
        return results
        # TODO
        #  add logic to customize the query
        #  add logic to track uptime
        #  add logic to track time since last player connection
