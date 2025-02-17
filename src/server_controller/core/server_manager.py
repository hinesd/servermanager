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
            error_message = 'Process validation failed.'
            #todo find more memory efficient approach
            stdout, stderr = await self.process.communicate()
            if stdout.decode():
                error_message += f"\nSTDOUT: {stdout.decode()[-500:]}"
            if stderr.decode():
                error_message += f"\nSTDERR: {stderr.decode()[-500:]}"
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
        await asyncio.to_thread(lambda: os.chmod(self.start_script, 0o755))

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
        self.server_properties = None
        self.query_connection = None

    async def init_server_properties(self):
        properties_path = self.process_manager.server_path + '/server.properties'
        if await asyncio.to_thread(os.path.exists, properties_path):
            self.server_properties = dict([x.split('=') for x in open(properties_path).read().strip().split('\n')[2:]])
        if not self.query_connection:
            self.query_connection = JavaServer(self.process_manager.server_domain,int(self.server_properties['server-port']), timeout=30)
        return None

    async def init_server_connection(self):
        timeout = self.process_manager.timeout
        increment = 3
        while timeout > 0:
            await self.process_manager.validate_process()
            if not self.query_connection:
                await self.init_server_properties()
            else:
                try:
                    return await self.query_connection.async_ping()
                except ConnectionRefusedError:
                    pass
                except ProcessValidationFailed as e:
                    await self.process_manager.stop()
                    raise e
                except Exception as e:
                    await self.process_manager.stop()
                    raise e
                finally:
                    await asyncio.sleep(increment)
                    timeout -= increment
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
