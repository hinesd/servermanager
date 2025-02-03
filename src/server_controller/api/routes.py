from fastapi import APIRouter, HTTPException
from api.core.minecraft import MinecraftServer
from exceptions.server_exceptions import ProcessDoesNotExist, ProcessAlreadyExistsError, ProcessCreationFailed

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
    except ProcessCreationFailed:
        return HTTPException(status_code=500 , detail=f"Server start script failed")
    except Exception as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code":200,"detail": status}


@router.get("/server/stop")
async def stop_server():
    global minecraft_server
    if minecraft_server is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await minecraft_server.stop()
    except ProcessDoesNotExist:
        return {"status_code": 500, "detail": 'No server to stop'}
    except Exception as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code":200,"detail": status}
