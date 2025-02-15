import uvicorn
from fastapi import APIRouter, HTTPException, FastAPI
from core.process_manager import ProcessManager, ProcessValidationFailed
from core.server_manager import ServerManager
from servermanager.settings.config import START_SCRIPT, SERVER_PATH, SERVER_DOMAIN, SERVER_TIMEOUT

router = APIRouter()
process_manager = None
server_manager = None

@router.get("/server/start")
async def start_server():
    global process_manager
    global server_manager
    if process_manager is not None:
        return {"status_code": 500, "detail": "Process Already Exists"}
    try:
        process_manager = ProcessManager(SERVER_PATH, START_SCRIPT, SERVER_DOMAIN, SERVER_TIMEOUT)
        server_manager = ServerManager(process_manager)
        await process_manager.start()
        await server_manager.init_server_connection()
    except (ProcessValidationFailed, FileNotFoundError, ConnectionRefusedError) as e:
        process_manager = None
        server_manager = None
        return {"status_code": 500, "detail": str(e)}

    return {"status_code": 200, "detail": 'Server Started'}

@router.get("/server/stop")
async def stop_server():
    global process_manager
    global server_manager
    if process_manager is None:
        return HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        await process_manager.stop()
    except (ProcessValidationFailed) as e:
        return {"status_code": 500, "detail": str(e)}
    finally:
        process_manager = None
        server_manager = None
    return {"status_code": 200, "detail": 'Server Stopped'}

@router.get("/server/status")
async def server_status(query: str | None = None):
    if process_manager is None:
        raise HTTPException(status_code=500, detail="Server has not been initialized")
    try:
        status = await server_manager.server_status(query)
    except ProcessValidationFailed as e:
        return {"status_code": 500, "detail": str(e)}
    return {"status_code": 200, "detail": status}

app = FastAPI()
app.include_router(router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)