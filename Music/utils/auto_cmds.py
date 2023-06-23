import datetime
import os
from Music.core.database import db
from Music.core.calls import hellmusic
from config import Config


async def autoend(chat_id: int):
    autoend = await db.get_autoend(chat_id)
    if autoend:
        users = len(await hellmusic.vc_participants(chat_id))
        if users == 1:
            db.autoend[chat_id] = datetime.datetime.now() + datetime.timedelta(minutes=5)
        else:
            db.autoend[chat_id] = {}


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