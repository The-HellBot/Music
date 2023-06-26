import asyncio
import datetime
import os

from pyrogram.types import Message

from config import Config
from Music.helpers.formatters import formatter

from .database import db
from .logger import LOGS


async def autoend(chat_id: int, client):
    autoend = await db.get_autoend()
    if autoend:
        users = len(await client.vc_participants(chat_id))
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


async def auto_delete(message: Message, duration: str):
    delay = formatter.mins_to_secs(duration)
    try:
        await asyncio.sleep(delay + 10)
        await message.delete()
    except Exception as e:
        LOGS.info(str(e))
