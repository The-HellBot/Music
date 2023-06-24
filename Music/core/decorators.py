from functools import wraps

from pyrogram.types import CallbackQuery, Message

from config import Config
from Music.utils.admins import get_auth_users

from .database import db

on_mode = ["on", "enable", "yes", "true"]


def check_mode(func):
    @wraps(func)
    async def decorated(client, message):
        if isinstance(message, Message):
            user_id = message.from_user.id
        elif isinstance(message, CallbackQuery):
            user_id = message.from_user.id
        else:
            return
        if (Config.PRIVATE_MODE).lower in on_mode:
            if user_id not in Config.SUDO_USERS:
                return
        await func(client, message)

    return decorated


def AdminsWrapper(func):
    @wraps(func)
    async def decorated(client, message):
        try:
            await message.delete()
        except:
            pass
        if message.sender_chat:
            return await message.reply_text(
                "Seems like you are an anonymous admin. Please revert back to normal to use this command."
            )
        chat_id = message.chat.id
        if not await db.is_active_vc(chat_id):
            return await message.reply_text("Nothing is streaming on the voice chat!")
        is_authchat = await db.get_authchats(message.chat.id)
        if not is_authchat:
            if message.from_user.id not in Config.SUDO_USERS:
                try:
                    admins = await get_auth_users(chat_id)
                except Exception as e:
                    return await message.reply_text(
                        f"There was an error while fetching admin list. Please try again later.\n\n`{e}`"
                    )
                if not admins:
                    return await message.reply_text(
                        "Need to refresh admin list. Click here -> /reload"
                    )
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(
                            "This command is only for authorized users and admins!"
                        )
        return await func(client, message, chat_id)

    return decorated
