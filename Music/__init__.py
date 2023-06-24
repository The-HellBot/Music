import os
import time

from config import Config
from Music.core.logger import LOGS


local_db = {}
__start_time__ = time.time()


# make required directories
if not os.path.isdir(Config.DWL_DIR):
    os.makedirs(Config.DWL_DIR)
if not os.path.isdir(Config.CACHE_DIR):
    os.makedirs(Config.CACHE_DIR)


# If any of the important variables are missing stop the bot from starting
if Config.API_ID == 0:
    LOGS.error("API ID is missing! Kindly check again!")
    quit(1)
if not Config.API_HASH:
    LOGS.error("API HASH is missing! Kindly check again!")
    quit(1)
if not Config.BOT_TOKEN:
    LOGS.error("BOT TOKEN is missing! Kindly check again!")
    quit(1)
if not Config.DATABASE_URL:
    LOGS.error("DATABASE URL is missing! Kindly check again!")
    quit(1)
if Config.LOGGER_ID == 0:
    LOGS.error("LOGGER ID is missing! Kindly check again!")
    quit(1)
if not Config.OWNER_ID:
    LOGS.error("OWNER ID is missing! Kindly check again!")
    quit(1)
if not Config.HELLBOT_SESSION:
    LOGS.error("HELLBOT SESSION is missing! Kindly check again!")
    quit(1)
