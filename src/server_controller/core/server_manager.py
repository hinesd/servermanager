from mcstatus import JavaServer
import asyncio
import os
import platform
from core.exceptions import *

class ProcessManager:

    def __init__(self, server_path, start_script, server_domain, timeout):
        self.server_path = server_path
        self.start_script = f"{server_path}/{start_script}"
        self.server_domain = server_domain
        self.timeout = timeout
        self.is_windows = platform.system() == "Windows"
        self.process = None

    async def validate_process(self):
        if not self.process:  # If no process
            raise ProcessDoesNotExist()
        if self.process.returncode is not None:  # If process is not running
            stdout, stderr = await self.process.communicate()
            error_message = f"Process validation failed:\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
            await self.kill_process()
            raise ProcessValidationFailed(error_message)

    async def kill_process(self):
        try:
            await self.process.communicate(input='stop\n'.encode('utf-8'))
            await asyncio.wait_for(self.process.wait(), timeout=5)
        except TimeoutError:
            self.process.kill()
            await self.process.wait()
        except ProcessLookupError:
            pass
        finally:
            self.process = None

    async def create_process(self):
        await asyncio.to_thread(lambda: os.chmod(self.server_path, 0o755))
        self.process = await asyncio.create_subprocess_shell(
            self.start_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            cwd=self.server_path,
        )

    async def start(self):
        if self.process:
            raise ProcessAlreadyExistsError()
        if not await asyncio.to_thread(os.path.exists, self.start_script):
            raise FileNotFoundError(self.start_script)
        try:
            await self.create_process()
            await asyncio.sleep(2)
            await self.validate_process()
        except ProcessValidationFailed as e:
            raise ProcessCreationFailed(e.message)

    async def stop(self):
        await self.validate_process()
        await self.kill_process()


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
