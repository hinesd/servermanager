import uvicorn
from fastapi import APIRouter, HTTPException, FastAPI
from core.exceptions import *
from core.server_manager import ProcessManager
from settings.config import START_SCRIPT, SERVER_PATH, SERVER_DOMAIN

router = APIRouter()
process_manager = ProcessManager(SERVER_PATH, START_SCRIPT, SERVER_DOMAIN)

@router.get("/server/start")
async def start_server():
    global process_manager
    message = {}
    status = 200

    try:
        await process_manager.start()
    except (FileNotFoundError, ProcessAlreadyExistsError) as e:
        message = {"error":e.message}
        status = 500
    except ProcessNotRunning:
        pass
    except Exception as e:
        raise e
    finally:
        if not message:
            output = await process_manager.get_logs()
            message = {'logs':output}

    result = {"status_code": status}
    result.update(message)
    return result

@router.get("/server/stop")
async def stop_server():
    global process_manager
    message = {}
    status = 200

    try:
        await process_manager.stop()
    except (ProcessDoesNotExist, CommandNotAllowed) as e:
        message = {"error": e.message}
        status = 500
    except ProcessNotRunning:
        pass
    finally:
        if not message:
            output = await process_manager.get_logs()
            message = {'logs': output}

    result = {"status_code": status}
    result.update(message)
    return result


@router.get("/server/status")
async def server_status(stdout: bool = False, stderr: bool = False, reverse: bool = False, consume: bool = False):
    status = 200
    output = await process_manager.get_logs(stdout=stdout, stderr=stderr, reverse=reverse, consume=consume)
    result = {"status_code": status, 'logs': output}
    return result


@router.get("/server/send_command")
async def send_command(command: str | None = None):
    global process_manager
    message = {}
    status = 200
    try:
        await process_manager.send_command(command)
    except (ProcessDoesNotExist, ProcessNotRunning, CommandNotAllowed) as e:
        message = {"error": e.message}
        status = 500
    finally:
        if not message:
            output = await process_manager.get_logs()
            message = {'logs': output}

    result = {"status_code": status}
    result.update(message)
    return result

app = FastAPI()
app.include_router(router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)