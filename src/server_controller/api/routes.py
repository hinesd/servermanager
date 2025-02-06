from fastapi import APIRouter, HTTPException
from typing import Optional
from server_controller.api.core.minecraft import MinecraftServer
from server_controller.exceptions.server_exceptions import ProcessDoesNotExist, ProcessAlreadyExistsError, ProcessCreationFailed

router = APIRouter()
minecraft_server = None

@router.get("/server/start")
async def start_server():
    global minecraft_server
    if minecraft_server is None:
        minecraft_server = MinecraftServer()
    try:
        status = await minecraft_server.start()
    except ProcessAlreadyExistsError:
        return HTTPException(status_code=500, detail="Server already running")
    except FileNotFoundError:
        return HTTPException(status_code=404, detail=f"{minecraft_server.start_script} not found")
    except ProcessCreationFailed as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code":200,"detail": status}


@router.get("/server/stop")
async def stop_server():
    global minecraft_server
    if minecraft_server is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await minecraft_server.stop()
    except ProcessDoesNotExist as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code":200,"detail": status}


@router.get("/server/status")
async def server_status(query: Optional[str] = None):
    global minecraft_server
    if minecraft_server is None:
        raise HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await minecraft_server.get_server_status(query)
    except ProcessDoesNotExist as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code": 200, "detail": status}


