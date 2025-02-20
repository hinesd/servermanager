from datetime import datetime, timedelta
from asyncio import sleep, wait_for, to_thread, create_subprocess_shell
from asyncio.subprocess import PIPE
import os
from core.exceptions import ProcessNotRunning, ProcessDoesNotExist, ProcessAlreadyExistsError, CommandNotAllowed
import logging

logging.basicConfig(level=logging.DEBUG)
allowed_commands = ['I agree', 'true', 'True', 'stop']

class ProcessManager:

    def __init__(self, server_path, start_script, server_domain, timeout=90):
        self.server_path = server_path
        self.start_script = f"{server_path}/{start_script}"
        self.server_domain = server_domain
        self.timeout = timeout
        self.process = None
        self.process_log_stdout = ''
        self.process_log_stderr = ''


    async def _process_log_stream(self):
        # todo figure out why initial create doesnt generate logs
        async def get_stream(stream):
            try:
                chunk = await wait_for(getattr(self.process, stream).read(1024), .1)  # Read 1KB at a time
                if chunk:
                    logging.debug(chunk)
                    new_log = self.process_log_stdout + chunk.decode()
                    setattr(self, f'process_log_{stream}', new_log)
                    
            except (ProcessLookupError, ConnectionResetError, TimeoutError):
                pass
        current_time = datetime.now()
        last_updated = datetime.now()
        while current_time - last_updated < timedelta(seconds=5):
            if await get_stream('stdout') or await get_stream('stderr'):
                last_updated = datetime.now()
            current_time = datetime.now()


    async def _validate_process_status(self):
        if not self.process_log_stdout:
            self.process_log_stdout = ''
        if not self.process_log_stderr:
            self.process_log_stderr = ''
        if not self.process:
            raise ProcessDoesNotExist()
        await self._process_log_stream()
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
        self.process = await create_subprocess_shell(f'bash {script}', stdin=PIPE,stdout=PIPE,stderr=PIPE,shell=True,cwd=self.server_path)
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


    async def get_logs(self, stdout=False, stderr=False, reverse=True, consume=False):
        try:
            await self._validate_process_status()
        except (ProcessNotRunning, ProcessDoesNotExist):
            pass
        if not self.process_log_stdout or not self.process_log_stderr:
            return "No Logs Found"
        stream_attribute = 'process_log_stdout' if stdout or not stdout and not stderr else 'process_log_stderr'
        if not getattr(self, stream_attribute):
            return f"No logs in {stream_attribute}. set 'stdout' or 'stderr' to True to find logs"
        if consume:
            output = getattr(self, stream_attribute)
            setattr(self, stream_attribute, None)
            return output
        output = getattr(self, stream_attribute)[-1000:] if reverse else getattr(self, stream_attribute)[:1000]
        setattr(self, stream_attribute, getattr(self, stream_attribute)[:-1000]) if reverse else setattr(self, stream_attribute, getattr(self, stream_attribute)[1000:])
        return output


    async def send_command(self, command):
        if command not in allowed_commands:
            raise CommandNotAllowed(command)
        await self._validate_process_status()
        self.process.stdin.write(f'{command}\n'.encode('utf-8'))
        await self._validate_process_status()


    async def start(self):
        await self._create_process(self.start_script)


    async def stop(self):
        await self._validate_process_status()
        await self._kill_process()
