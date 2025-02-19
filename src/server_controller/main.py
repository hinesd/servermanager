import uvicorn
from fastapi import APIRouter, HTTPException, FastAPI
from core.exceptions import *
from core.server_manager import ServerManager, ProcessManager
from settings.config import START_SCRIPT, SERVER_PATH, SERVER_DOMAIN, ADDITIONAL_INSTALL_SCRIPT

router = APIRouter()
process_manager = None
server_manager = None


@router.get("/server/start")
async def start_server():
    global process_manager
    global server_manager
    if not process_manager:
        process_manager = ProcessManager(SERVER_PATH, START_SCRIPT, SERVER_DOMAIN, ADDITIONAL_INSTALL_SCRIPT)
        server_manager = ServerManager(process_manager)

    message = None
    status = 200

    try:
        await process_manager.start()
    except (FileNotFoundError, NoAdditionalScript) as e:
        message = {"error":e.message}
        status = 500
    except (ProcessNotRunning, ProcessCreationFailed):
        status = 200
    finally:
        if not message:
            try:
                process_log_out, process_log_err = await process_manager.process_status()
                message = {"stdout": process_log_out, "stderr": process_log_err}
            except ProcessDoesNotExist as e:
                message = {"error": e.message}
                status = 500
    result = {"status_code": status}
    result.update(message)
    return result


@router.get("/server/additional_install")
async def additional_install():
    global process_manager
    global server_manager
    if not process_manager:
        process_manager = ProcessManager(SERVER_PATH, START_SCRIPT, SERVER_DOMAIN, ADDITIONAL_INSTALL_SCRIPT)
        server_manager = ServerManager(process_manager)

    message = None
    status = 200
    try:
        await process_manager.additional_install()
    except (ProcessNotRunning, ProcessCreationFailed, FileNotFoundError, NoAdditionalScript) as e:
        message = {"error": e.message}
        status = 500
    except LongRunningProcess:
        status = 102
    finally:
        if not message:
            try:
                process_log_out, process_log_err = await process_manager.process_status()
                message = {"stdout": process_log_out, "stderr": process_log_err}
            except ProcessDoesNotExist as e:
                message = {"error": e.message}
                status = 500
    result = {"status_code": status}
    result.update(message)
    return result
@router.get("/server/stop")
async def stop_server():
    global process_manager
    global server_manager
    if process_manager is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")
    message = None
    status = 200
    try:
        await process_manager.stop()
        process_manager = None
        server_manager = None
    except (ProcessValidationFailed) as e:
        message = {"error": e.message}
        status = 500
    finally:
        if not message:
            try:
                process_log_out, process_log_err = await process_manager.process_status()
                message = {"stdout": process_log_out, "stderr": process_log_err}
            except ProcessDoesNotExist as e:
                message = {"error": e.message}
                status = 500
    result = {"status_code": status}
    result.update(message)
    return result

@router.get("/server/status")
async def server_status(query: str | None = None):
    if process_manager is None:
        raise HTTPException(status_code=500, detail="Server has not been initialized")
    message = None
    status = 200
    try:
        process_log_out, process_log_err = await process_manager.process_status()
    except ProcessDoesNotExist as e:
        message = {"error": e.message}
        status = 500
    except LongRunningProcess:
        status = 102
    except ProcessNotRunning:
        status = 200
    finally:
        if not message:
            try:
                process_log_out, process_log_err = await process_manager.process_status()
                message = {"stdout": process_log_out, "stderr": process_log_err}
            except ProcessDoesNotExist as e:
                message = {"error": e.message}
                status = 500
    result = {"status_code": status}
    result.update(message)
    return result

@router.get("/server/send_command")
async def send_command(command: str | None = None):
    if process_manager is None:
        raise HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        process_log_out, process_log_err = await process_manager.send_command(command)
    except CommandNotAllowed as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code": 200, "stdout": process_log_out, "stderr": process_log_err}

app = FastAPI()
app.include_router(router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)