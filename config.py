import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
DEBUG = os.getenv('DEBUG') == 'True'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TS_AUTHKEY = os.getenv('TS_AUTHKEY')
SERVER_DNS = os.getenv('SERVER_DNS')
CONTAINER_NAME=os.getenv('CONTAINER_NAME')
TAILSCALE_TAG=os.getenv('TAILSCALE_TAG')
EPHEMERAL_MODE=os.getenv('EPHEMERAL_MODE')
NAME = os.getenv('NAME')
