import asyncio
import datetime
import os
import time
import traceback

import aiofiles
from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked
from pyrogram.types import Message

from Music.core.database import db

from .formatters import formatter


class Broadcast:
    def __init__(self) -> None:
        self.file_name = "broadcast_{0}.txt"

    async def send_msg(self, user_id: int, message: Message, copy: bool):
        try:
            if copy is False:
                await message.forward(chat_id=user_id)
            elif copy is True:
                await message.copy(chat_id=user_id)
            return 200, None
        except FloodWait as e:
            await asyncio.sleep(e.x)
            return self.send_msg(user_id, message, copy)
        except InputUserDeactivated:
            return 400, f"{user_id} -:- deactivated\n"
        except UserIsBlocked:
            return 400, f"{user_id} -:- blocked the bot\n"
        except PeerIdInvalid:
            return 400, f"{user_id} -:- user id invalid\n"
        except Exception:
            return 500, f"{user_id} -:- {traceback.format_exc()}\n"

    async def broadcast(self, message: Message, type: str, copy: bool):
        targets = []
        if type == "chats":
            target = await db.get_all_chats()
            count = await db.total_chats_count()
            targets.append(target)
        elif type == "users":
            target = await db.get_all_users()
            count = await db.total_users_count()
            targets.append(target)
        elif type == "all":
            targets_u = await db.get_all_users()
            targets_c = await db.get_all_chats()
            count_u = await db.total_users_count()
            count_c = await db.total_chats_count()
            targets.append(targets_u)
            targets.append(targets_c)
            count = count_u + count_c

        broadcast_msg = message.reply_to_message
        out = await message.reply_text(
            text=f"**Starting broadcast ...** \n\nYou'll get the log file after it's finised."
        )
        start_time = time.time()
        done = 0
        failed = 0
        success = 0
        file_name = self.file_name.format(round(time.time()))
        async with aiofiles.open(file_name, "w") as broadcast_log_file:
            for target in targets:
                async for user in target:
                    try:
                        sts, msg = await self.send_msg(
                            int(user["user_id"]),
                            broadcast_msg,
                            copy,
                        )
                    except KeyError:
                        sts, msg = await self.send_msg(
                            int(user["chat_id"]),
                            broadcast_msg,
                            copy,
                        )
                    except Exception:
                        pass
                    if msg is not None:
                        await broadcast_log_file.write(msg)
                    if sts == 200:
                        success += 1
                    else:
                        failed += 1
                    done += 1
        completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
        await asyncio.sleep(3)
        await out.delete()
        success_text = (
            "__Broadcast completed successfully!__\n\n"
            f"**Chats in DB:** `{count} chats` \n**Gcast Iterations:** `{done} loops` \n**Gcasted in:** `{success} chats` \n**Failed in:** `{failed} chats` \n**Completed in:** `{completed_in}`"
        )
        if failed == 0:
            await message.reply_text(
                text=success_text,
                quote=True,
            )
        else:
            log_text = ""
            with open(file_name, "r") as _file:
                log_text = _file.read()
            link = await formatter.bb_paste(log_text)
            await message.reply_document(
                document=file_name,
                caption=success_text + f"\n\n**Error log:** [here]({link})",
                quote=True,
            )
        os.remove(file_name)


Gcast = Broadcast()
