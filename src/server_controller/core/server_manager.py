from datetime import datetime, timedelta
from asyncio import sleep, wait_for, to_thread, create_subprocess_shell, Queue, QueueEmpty
from asyncio.subprocess import PIPE, STDOUT
import os
import gzip
import aiofiles
from core.exceptions import ProcessNotRunning, ProcessDoesNotExist, ProcessAlreadyExistsError, CommandNotAllowed
import logging

logging.basicConfig(level=logging.DEBUG)
allowed_commands = {'I agree', 'true', 'True', 'stop'}


def write_gzip(gzip_file_path, output):
    with gzip.open(gzip_file_path, 'wb') as gz:
        gz.write(output.encode('utf-8'))


class ProcessManager:

    def __init__(self, root_path, start_script, server_domain, timeout=90):
        self.root_path = root_path
        self.server_path = f"{root_path}/server"
        self.log_path = f"{root_path}/logs"
        self.log_file_path = f"{self.log_path}/latest.log"
        self.start_script = f"{self.server_path}/{start_script}"
        self.server_domain = server_domain
        self.timeout = timeout
        self.process = None
        self.process_log = Queue()


    async def _process_log_stream(self):
        current_time = datetime.now()
        last_updated = datetime.now()
        new_logs = ''
        while current_time - last_updated < timedelta(seconds=5):
            try:
                chunk = await wait_for(self.process.stdout.read(128), .1)
                if chunk:
                    logging.debug(chunk)
                    new_logs = new_logs + chunk.decode()
                    last_updated = datetime.now()
            except TimeoutError:
                pass
            except (ProcessLookupError, ConnectionResetError):
                break
            current_time = datetime.now()
            await sleep(.05)
        await self.process_log.put(new_logs)


    async def _dump_logs(self):
        try:
            logs = self.process_log.get_nowait()
            while logs:
                async with aiofiles.open(self.log_file_path, 'a') as file:
                    await file.write(logs)
                logs = self.process_log.get_nowait()
        except QueueEmpty:
            pass


    async def _flush_logs(self):
        # Ensure the file is empty before processing new logs
        async with aiofiles.open(self.log_file_path, 'r') as file:
            output = await file.read()
            if output:
                gzip_file_path = f"{self.log_path}/logs_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.gz"
                await to_thread(write_gzip, gzip_file_path, output)
        async with aiofiles.open(self.log_file_path, 'w') as file:
            await file.write('')


    async def _validate_process_status(self):
        if not self.process:
            raise ProcessDoesNotExist()
        await self._process_log_stream()
        await self._dump_logs()
        if self.process.returncode is not None:
            try:
                self.process.kill()
                await self.process.wait()
            except ProcessLookupError:
                pass
            raise ProcessNotRunning()


    async def _create_process(self, script):
        if not await to_thread(os.path.exists, script):
            raise FileNotFoundError(script)
        if self.process:
            raise ProcessAlreadyExistsError()
        await self._flush_logs()
        self.process = await create_subprocess_shell(f'bash {script}', stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True, cwd=self.server_path, start_new_session=True)
        await sleep(3)
        await self._validate_process_status()


    async def _kill_process(self, graceful=True):
        try:
            if graceful:
                await self.send_command('stop')
            else:
                self.process.kill()
            await wait_for(self.process.wait(), timeout=10)
        except TimeoutError:
            self.process.kill()
            await self.process.wait()
        except ProcessLookupError:
            pass
        finally:
            self.process = None


    async def send_command(self, command):
        #todo improve/secure terminal access
        if command not in allowed_commands:
            raise CommandNotAllowed(command)
        await self._validate_process_status()
        self.process.stdin.write(f'{command}\n'.encode('utf-8'))
        await self.process.stdin.drain()
        await sleep(1)
        await self._validate_process_status()


    async def start(self):
        await self._create_process(self.start_script)


    async def stop(self):
        await self._validate_process_status()
        await self._kill_process()


    async def get_logs(self):
        # Read logs from the log file
        try:
            await self._validate_process_status()
        except (ProcessNotRunning, ProcessDoesNotExist):
            pass
        try:
            async with aiofiles.open(self.log_file_path, 'r') as file:
                output = await file.read()
            if not output:
                return "No Logs Found"
            return output
        except FileNotFoundError:
            return "Log file not found"
