import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
DEBUG = os.getenv('DEBUG') == 'True'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TS_AUTHKEY = os.getenv('TS_AUTHKEY')
SERVER_DOMAIN = os.getenv('SERVER_DOMAIN')
