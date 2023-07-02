import asyncio
import datetime
import os
import time
import traceback

import aiofiles
from pyrogram.errors import FloodWait, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup

from config import Config
from Music.core.database import db


class Leaderboard:
    def __init__(self) -> None:
        self.file_name = "leaderboard.txt"

    def get_hrs(self) -> int:
        try:
            hrs = int(Config.LEADERBOARD_TIME.split(":")[0])
        except:
            hrs = 3
        return hrs

    def get_min(self) -> int:
        try:
            mins = int(Config.LEADERBOARD_TIME.split(":")[1])
        except:
            mins = 0
        return mins

    async def get_top_10(self) -> list:
        users = await db.get_all_users()
        all_guys = []
        async for user in users:
            id = int(user["user_id"])
            songs = int(user["songs_played"])
            user_name = user["user_name"]
            context = {"id": id, "songs": songs, "user": user_name}
            all_guys.append(context)
        all_guys = sorted(all_guys, key=lambda x: x["songs"], reverse=True)
        top_10 = all_guys[:10]
        return top_10

    async def generate(self, bot_details: dict) -> str:
        index = 0
        top_10 = await self.get_top_10()
        text = f"**🧡 Top 10 Users of {bot_details['mention']}**\n\n"
        hellbot = bot_details["client"]
        for top in top_10:
            index += 1
            link = f"https://t.me/{bot_details['username']}?start=user_{top['id']}"
            text += f"**⤷ {'0' if index <= 9 else ''}{index}:** [{top['user']}]({link})\n"
        text += "\n**🧡 Enjoy Streaming! Have Fun!**"
        return text

    async def broadcast(self, hellbot, text, buttons):
        start = time.time()
        success = failed = count = 0
        chats = await db.get_all_chats()
        async with aiofiles.open(self.file_name, mode="w") as leaderboard_log_file:
            async for chat in chats:
                try:
                    sts, msg = await self.send_message(
                        hellbot.app, buttons, int(chat["chat_id"]), text
                    )
                except Exception:
                    pass
                if msg is not None:
                    await leaderboard_log_file.write(msg)
                if sts == 1:
                    success += 1
                else:
                    failed += 1
                count += 1
                await asyncio.sleep(0.3)
        time_taken = datetime.timedelta(seconds=int(time.time() - start))
        await asyncio.sleep(3)
        to_log = f"**Leaderboard Auto Broadcast Completed in** `{time_taken}`\n\n**Total Chats:** `{count}`\n**Success:** `{success}`\n**Failed:** `{failed}`\n\n**🧡 Enjoy Streaming! Have Fun!**"
        if failed == 0:
            await hellbot.logit("leaderboard", to_log)
        else:
            await hellbot.logit("leaderboard", to_log, self.file_name)
        os.remove(self.file_name)

    async def send_message(self, hellbot, buttons, chat: int, text: str):
        try:
            await hellbot.send_message(
                chat,
                text,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True,
            )
            return 1, None
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await self.send_message(hellbot, buttons, chat, text)
        except PeerIdInvalid:
            return 2, f"{chat} -:- chat id invalid\n"
        except Exception:
            return 3, f"{chat} -:- {traceback.format_exc()}\n"


leaders = Leaderboard()
