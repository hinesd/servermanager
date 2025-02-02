from fastapi import APIRouter, HTTPException
from core.minecraft import MinecraftServer
from server_controller.exceptions.server_exceptions import ProcessDoesNotExist, ProcessAlreadyExistsError, ProcessStartFailed

router = APIRouter()
minecraft_server = None

@router.get("/server/start")
async def start_server():
    global minecraft_server
    if minecraft_server is None:
        minecraft_server = MinecraftServer()

    try:
        status = await minecraft_server.start(create_process=True)

    except ProcessAlreadyExistsError:
        return HTTPException(status_code=500, detail="Server already running")
    except FileNotFoundError:
        return HTTPException(status_code=404, detail=f"{minecraft_server.start_script} not found")
    except ProcessStartFailed:
        return HTTPException(status_code=500 , detail=f"Server failed to start")

    return {"status": status}


@router.get("/server/stop")
async def stop_server():
    global minecraft_server
    if minecraft_server is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")

    try:
        status = await minecraft_server.stop()
    except ProcessDoesNotExist:
        raise HTTPException(status_code=500, detail="No server to stop")

    return {"status": status}
