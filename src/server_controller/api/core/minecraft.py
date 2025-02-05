import os
from mcrcon import MCRcon
from mcstatus import JavaServer
import json
from asyncio import create_subprocess_shell, wait_for, to_thread, sleep
from asyncio.subprocess import PIPE
from pathlib import Path
from server_controller.exceptions.server_exceptions import *
from config import ENV_NAME, SERVER_DNS


class MinecraftServer:

    def __init__(self):
        self.process = None
        self.base_path = next(p for p in Path(__file__).resolve().parents if p.name == 'server_controller')
        self.server_path = f'{self.base_path}/server' if ENV_NAME == 'prod' else f'{self.base_path}/testserver/'
        self.start_script = f'{self.server_path}/start_script.sh'
        #TODO add logic to dynamically override server.properties using attributes defined in config.py
        self.server_properties = dict([x.split('=') for x in open(self.server_path + 'server.properties').read().strip().split('\n')[2:]])


    async def kill_process(self):
        try:
            self.process.kill()
            await self.process.wait()
        except ProcessLookupError:
            pass
        finally:
            self.process = None


    async def graceful_shutdown(self):
        try:
            self.process.stdin.write(b'stop\n')
            await self.process.stdin.drain()
            await wait_for(self.process.wait(), timeout=5)
        except TimeoutError:
            await self.kill_process()
        finally:
            self.process = None


    async def process_validation(self):
        if not self.process:
            raise ProcessDoesNotExist()
        if self.process.returncode is not None:
            stdout, stderr = await self.process.communicate()
            error_message = f"Process validation failed:\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
            await self.kill_process()
            raise ProcessCreationFailed(error_message)


    async def validate_or_create_process(self, create_process=None):
        if self.process and create_process:
            raise ProcessAlreadyExistsError()
        if create_process:
            await to_thread(lambda: os.chmod(self.start_script, 0o755))
            self.process = await create_subprocess_shell(self.start_script,stdin=PIPE,stdout=PIPE,stderr=PIPE,cwd=self.server_path)
            await sleep(1)
        await self.process_validation()


    async def get_server_status(self):
        # todo this test is temporary, need to be cleaned up to make a bit more sense
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            try:
                server = JavaServer(SERVER_DNS, int(self.server_properties.get('query.port', 25565)))
                return json.dumps(server.status().raw)
            except ConnectionRefusedError:
                await sleep(5)
        await self.graceful_shutdown()
        raise ConnectionRefusedError


    async def start(self, create_process=None):
        #todo add logic to make sure port is not taken already to accound for this error
        """Failed to start the minecraft server ./world/session.lock: already locked (possibly by other Minecraft instance?)"""
        if not os.path.exists(self.start_script):
            raise FileNotFoundError(self.start_script)
        await self.validate_or_create_process(create_process=create_process)
        #todo make this server connection test make more sense
        server_status = await self.get_server_status()
        return 'Server Successfully Started\n' + server_status


    async def stop(self):
        await self.validate_or_create_process()
        await self.graceful_shutdown()
        return "Successfully Stopped Server"
