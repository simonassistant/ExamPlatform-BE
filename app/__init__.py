# Environment
import logging
import os
from dotenv import find_dotenv, load_dotenv

env_state = os.getenv("ENV_STATE")
load_dotenv(find_dotenv(), override=True)
load_dotenv(find_dotenv(f".env.{env_state}"), override=True)

# Logging
import sys
logging.basicConfig(stream=sys.stdout, level=os.getenv("LOG_LEVEL", logging.ERROR))
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
