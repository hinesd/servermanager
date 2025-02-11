import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TS_AUTHKEY = os.getenv('TS_AUTHKEY')
SERVER_DNS = os.getenv('SERVER_DNS')
CONTAINER_NAME=os.getenv('CONTAINER_NAME')
TAILSCALE_TAG=os.getenv('TAILSCALE_TAG')
EPHEMERAL_MODE=os.getenv('EPHEMERAL_MODE')
ENV_NAME = os.getenv('ENV_NAME')
START_SCRIPT = 'start_script.sh'
SERVER_CONNECTION_RETRIES = 30