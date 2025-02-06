import os
from mcstatus import JavaServer
import datetime
from asyncio import create_subprocess_shell, wait_for, to_thread, sleep
from asyncio.subprocess import PIPE
from pathlib import Path
from server_controller.exceptions.server_exceptions import *
from config import ENV_NAME, SERVER_DNS


class MinecraftServer:

    def __init__(self):
        self.process = None
        self.server_connection = None
        self.created_at = datetime.datetime.now()
        self.base_path = next(p for p in Path(__file__).resolve().parents if p.name == 'server_controller')
        self.server_path = f'{self.base_path}/server' if ENV_NAME == 'prod' else f'{self.base_path}/testserver/'
        self.start_script = f'{self.server_path}/start_script.sh'
        self.server_properties = self._init_server_properties()
        self.server_port = int(self.server_properties['server-port'])


    def _init_server_properties(self):
        # TODO
        #  add logic to dynamically override server.properties using attributes defined in config.py before load
        #  add logic to dynamically load start_script configs into settings.sh defined in config.py before load
        return dict([x.split('=') for x in open(self.server_path + 'server.properties').read().strip().split('\n')[2:]])


    async def kill_process(self):
        try:
            self.process.kill()
            await self.process.wait()
        except ProcessLookupError:
            pass
        finally:
            self.process = None
            self.server_connection = None


    async def graceful_shutdown(self):
        try:
            self.process.stdin.write(b'stop\n')
            await self.process.stdin.drain()
            await wait_for(self.process.wait(), timeout=5)
        except TimeoutError:
            await self.kill_process()
        finally:
            self.process = None
            self.server_connection = None


    async def process_validation(self, create_process=None):
        if not self.process:
            raise ProcessDoesNotExist()
        if self.process.returncode is not None:
            # Is the process running
            stdout, stderr = await self.process.communicate()
            error_message = f"Process validation failed:\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
            await self.kill_process()
            raise ProcessValidationFailed(error_message)
        if create_process and not self.server_connection:
            self.server_connection = JavaServer(SERVER_DNS, self.server_port, timeout=30)
        max_retries = 10
        while max_retries:
            try:
                await self.server_connection.async_ping()
                return
            except ConnectionRefusedError:
                await sleep(10)
                max_retries -= 1
        raise ConnectionRefusedError()


    async def start(self):
        if not os.path.exists(self.start_script):
            #TODO
            # validate environment before starting server
            # ensure JAVA is installed
            # ensure a server.jar exists
            # Maybe this validation should happen in the system build step?
            raise FileNotFoundError(self.start_script)
        if self.process:
            raise ProcessAlreadyExistsError()
        await to_thread(lambda: os.chmod(self.start_script, 0o755))
        self.process = await create_subprocess_shell(self.start_script, stdin=PIPE, stdout=PIPE, stderr=PIPE,cwd=self.server_path)
        await sleep(1)
        try:
            await self.process_validation(create_process=True)
        except ProcessValidationFailed:
            raise ProcessCreationFailed()
        return f'Server successfully started'


    async def stop(self):
        await self.process_validation()
        await self.graceful_shutdown()
        return "Successfully Stopped Server"


    async def get_server_status(self, query=None):
        await self.process_validation()
        results = (await self.server_connection.async_status()).__dict__
        return results
        # TODO
        #  add logic to customize the query
        #  add logic to track uptime
        #  add logic to track time since last player connection
