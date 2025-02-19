from mcstatus import JavaServer
from datetime import datetime, timedelta
import asyncio
import os
from core.exceptions import *
import logging

from server_controller.core.exceptions import ProcessNotRunning

logging.basicConfig(level=logging.DEBUG)
allowed_commands = ['I agree', 'true', 'True', 'stop']

class ProcessManager:

    def __init__(self, server_path, start_script, server_domain, install_script=None, timeout=90):
        self.server_path = server_path
        self.start_script = f"{server_path}/{start_script}"
        self.install_script = f"{server_path}/{install_script}" if install_script else None
        self.server_domain = server_domain
        self.timeout = timeout
        self.process = None
        self.process_log_out = ''
        self.process_log_err = ''



    async def process_log_stream(self):
        async def get_logs():
            out = ''
            err = ''
            try:
                chunk = await asyncio.wait_for(self.process.stdout.read(1024), .1)  # Read 1KB at a time
                out += chunk.decode()
            except (ProcessLookupError, ConnectionResetError, TimeoutError):
                pass
            try:
                chunk = await asyncio.wait_for(self.process.stderr.read(1024), .1)  # Read 1KB at a time
                err += chunk.decode()
            except (ProcessLookupError, ConnectionResetError, TimeoutError):
                pass
            if out:
                logging.debug(out)
                self.process_log_out += out
            if err:
                logging.debug(err)
                self.process_log_err += err
            if out or err:
                return True

        last_updated = datetime.now()
        current_time = datetime.now()
        timeout = current_time + timedelta(seconds=self.timeout)

        while current_time < timeout and current_time - last_updated < timedelta(seconds=5):
            if await get_logs():
                last_updated = datetime.now()
            current_time = datetime.now()

        if datetime.now() > timeout:
            raise LongRunningProcess()


    async def validate_process_status(self):
        if not self.process:
            raise ProcessDoesNotExist()

        try:
            await self.process_log_stream()
        except LongRunningProcess:
            raise LongRunningProcess()

        if self.process.returncode is not None:
            try:
                self.process.kill()
                await self.process.wait()
            except ProcessLookupError:
                pass
            raise ProcessNotRunning()


    async def create_process(self, script):
        if not await asyncio.to_thread(os.path.exists, script):
            raise FileNotFoundError(script)
        if self.process:
            raise ProcessAlreadyExistsError()

        self.process = await asyncio.create_subprocess_shell(
            f'bash {script}', stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,shell=True,cwd=self.server_path,
        )

        try:
            await asyncio.sleep(3)
            await self.validate_process_status()
        except ProcessNotRunning:
            if script != self.install_script:
                raise ProcessCreationFailed()
            raise ProcessNotRunning()


    async def send_command(self, command):
        if command not in allowed_commands:
            raise CommandNotAllowed(command)
        await self.validate_process_status()
        self.process.stdin.write(f'{command}\n'.encode('utf-8'))
        try:
            await self.validate_process_status()
        except ProcessNotRunning:
            pass


    async def kill_process(self):
        try:
            await self.send_command('stop')
            await asyncio.wait_for(self.process.wait(), timeout=3)
        except TimeoutError:
            self.process.kill()
            await self.process.wait()
        except ProcessLookupError:
            pass
        finally:
            self.process = None


    async def additional_install(self):
        try:
            await self.create_process(self.install_script)
        except LongRunningProcess:
            raise LongRunningProcess("Additional install is still running")


    async def start(self):
        await self.create_process(self.start_script)


    async def stop(self):
        try:
            await self.validate_process_status()
        except (LongRunningProcess, ProcessNotRunning):
            pass
        await self.kill_process()


    async def process_status(self):
        try:
            await self.validate_process_status()
        except ProcessNotRunning:
            pass
        # consume logs
        process_log_out = None
        process_log_err = None
        if self.process_log_out:
            process_log_out = self.process_log_out[:1000]
            self.process_log_out = self.process_log_out[1000:]
        if self.process_log_err:
            process_log_err = self.process_log_err[:1000]
            self.process_log_err = self.process_log_err[1000:]

        return process_log_out, process_log_err

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
            await self.process_manager.validate_process_status()
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
        await self.process_manager.validate_process_status()
        results = (await self.query_connection.async_status()).__dict__
        return results
        # TODO
        #  add logic to customize the query
        #  add logic to track uptime
        #  add logic to track time since last player connection
