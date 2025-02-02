import subprocess
import os
from mcrcon import MCRcon
import asyncio
from server_controller.exceptions.server_exceptions import ProcessDoesNotExist, ProcessAlreadyExistsError


class MinecraftServer:

    def __init__(self):
        self.server_path = 'server'
        self.process = None
        self.start_script = 'server/start.bat'
        #todo build out for more custom/dynamic server initialization

        #todo fail initialization if server files do no exist in server directory


    def get_or_create_process(self, create_process=None) -> subprocess.Popen:

        def instantiate_process():
            #todo this could be more verbose
            return subprocess.Popen([self.start_script], shell=True, stdin=subprocess.PIPE)

        if self.process and create_process:
            raise ProcessAlreadyExistsError()
        if create_process:
            self.process = instantiate_process()
            return self.process

        if self.process:
            return self.process
        else:
            raise ProcessDoesNotExist()


    def is_running(self) -> bool:
        # TODO check the minecraft server itself using MCRcon, not just the process
        return self.get_or_create_process() is not None


    async def _kill_process(self):
        self.process.stdin.write(b'stop\n')
        self.process.stdin.flush()
        await asyncio.sleep(5)
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process = None


    async def start(self, create_process=None):
        if  not os.path.exists(self.start_script):
            raise FileNotFoundError(self.start_script)
        try:
            self.process = self.get_or_create_process(create_process=create_process)
        except ProcessAlreadyExistsError:
            raise Exception('Server has already been started')
        except Exception as e:
            raise e

        #todo check is_running until it returns True
        return 'Server Successfully Started'


    async def stop(self):
        try:
            self.get_or_create_process()
        except ProcessDoesNotExist:
            raise Exception('Server does not exist')
        await self._kill_process()
        return "Successfully Stopped Server"

