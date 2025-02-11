import asyncio
from pathlib import Path
from config import ENV_NAME
import os
import platform


class ProcessManager:

    def __init__(self, start_script):
        self.base_path = next(p for p in Path(__file__).resolve().parents if p.name == 'server_controller')
        self.server_path = f'{self.base_path}/server' if ENV_NAME == 'prod' else f'{self.base_path}/testserver'
        self.start_script = f'{self.server_path}/{start_script}'
        self.is_windows = platform.system() == "Windows"
        self.process = None

    async def validate_process(self):
        if not self.process: # If no process
            raise ProcessDoesNotExist()
        if self.process.returncode is not None: # If process is not running
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

        if self.is_windows:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.get_running_loop()
            protocol_factory = lambda: asyncio.subprocess.SubprocessStreamProtocol(limit=2 ** 16, loop=loop)
            self.process = await loop.subprocess_shell(
                protocol_factory,
                self.start_script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.server_path,
            )
        else:
            self.process = await asyncio.create_subprocess_shell(
                self.start_script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
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


class ProcessCreationFailed(Exception):
    def __init__(self, message="Process Creation Failed"):
        self.message = message
        super().__init__(self.message)

class ProcessDoesNotExist(Exception):
    def __init__(self, message="Process Does Not Exist"):
        self.message = message
        super().__init__(self.message)

class ProcessAlreadyExistsError(Exception):
    def __init__(self, message="Process Already Exists"):
        self.message = message
        super().__init__(self.message)

class ProcessValidationFailed(Exception):
    def __init__(self, message='Process Validation Failed'):
        self.message = message
        super().__init__(self.message)
