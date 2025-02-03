import subprocess
import os
from mcrcon import MCRcon
import asyncio
import time
from pathlib import Path
from exceptions.server_exceptions import ProcessDoesNotExist, ProcessAlreadyExistsError, ProcessCreationFailed


class MinecraftServer:

    def __init__(self):
        self.process = None
        self.base_path = next(p for p in Path(__file__).resolve().parents if p.name == 'server_controller')
        self.start_script = f'{self.base_path}/server/start.bat'


    def get_or_create_process(self, create_process=None) -> subprocess.Popen:

        if self.process and create_process:
            raise ProcessAlreadyExistsError()

        if create_process:
            os.chmod(self.start_script, 0o755)
            process = subprocess.Popen([self.start_script], shell=True, stdin=subprocess.PIPE)
            time.sleep(1)
            if process.poll() is not None:
                raise ProcessCreationFailed()
            return process

        if self.process:
            if self.process.poll() is not None:
                self.process.kill()
                self.process.wait()
                self.process = None
                raise ProcessDoesNotExist()
            return self.process
        else:
            raise ProcessDoesNotExist()


    def is_running(self) -> bool:
        # TODO check the minecraft server itself using MCRcon, not just the process
        return self.get_or_create_process() is not None


    async def start(self, create_process=None):
        if  not os.path.exists(self.start_script):
            raise FileNotFoundError(self.start_script)
        try:
            self.process = self.get_or_create_process(create_process=create_process)
        except ProcessAlreadyExistsError:
            raise ProcessAlreadyExistsError()
        except ProcessCreationFailed:
            raise ProcessCreationFailed()
        except Exception as e:
            raise e
        #todo process validation is still required, currently dont know if this is a valid process
        #todo check is_running until it returns True
        return 'Server Successfully Started'


    async def graceful_shutdown(self):
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


    async def stop(self):
        try:
            self.get_or_create_process()
        except ProcessDoesNotExist:
            raise ProcessDoesNotExist()
        except Exception as e:
            raise e
        await self.graceful_shutdown()
        return "Successfully Stopped Server"

