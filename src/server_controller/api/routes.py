from fastapi import APIRouter, HTTPException
from server_controller.core.process_manager import *
from config import START_SCRIPT

router = APIRouter()
process_manager = None
server_manager = None

@router.get("/server/start")
async def start_server():
    global process_manager
    if process_manager is None:
        process_manager = ProcessManager(START_SCRIPT)
    try:
        status = await process_manager.start()
    except (ProcessValidationFailed, ProcessStateValidationFailed, FileNotFoundError) as e:
        return {"status_code": 500, "detail": str(e)}
    if status == 'Running':
        return {"status_code": 200, "detail": 'Server Started'}
    else:
        return {"status_code": 200, "detail": f"Unexepected Process Status :{status}"}


@router.get("/server/stop")
async def stop_server(force: bool | None = None):
    global process_manager
    if process_manager is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await process_manager.stop(force=force)
    except (ProcessValidationFailed, ProcessStateValidationFailed) as e:
        return {"status_code": 500, "detail": str(e)}
    if status == 'DoesNotExist':
        return {"status_code": 200, "detail": 'Server Stopped'}
    else:
        return {"status_code": 200, "detail": f"Unexepected Process Status :{status}"}


@router.get("/server/status")
async def server_status(query: str | None = None):
    global minecraft_server
    if minecraft_server is None:
        raise HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await minecraft_server.server_status(query)
    except (ProcessValidationFailed, ProcessStateValidationFailed) as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code": 200, "detail": status}


