import os
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_ip_address():
    """
    Get the IP address of the current system/container.
    """
    if os.path.exists('/.dockerenv'):
        return 'server-controller'
    else:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception as e:
            raise e

# Access environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TS_AUTHKEY = os.getenv('TS_AUTHKEY')
TAILSCALE_TAG=os.getenv('TAILSCALE_TAG')
SERVER_DOMAIN = os.getenv('SERVER_DNS', get_ip_address())
ENV_NAME = os.getenv('ENV_NAME')
START_SCRIPT = 'start_script.sh'
SERVER_PATH = f"{Path(__file__).resolve().parent.parent}/server"
SERVER_TIMEOUT = 120