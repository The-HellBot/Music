import datetime
import os


from config import Config

from .database import db


async def autoend(chat_id: int, users: int):
    autoend = await db.get_autoend()
    if autoend:
        if users == 1:
            db.inactive[chat_id] = datetime.datetime.now() + datetime.timedelta(minutes=5)
        else:
            db.inactive[chat_id] = {}


async def autoclean(popped: dict):
    try:
        file = popped["file"]
        Config.CACHE.remove(file)
        count = Config.CACHE.count(file)
        if count == 0:
            try:
                os.remove(file)
            except:
                pass
    except:
        pass
