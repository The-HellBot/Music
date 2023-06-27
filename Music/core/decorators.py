from functools import wraps

from config import Config
from Music.utils.admins import get_auth_users, get_user_rights
from Music.utils.exceptions import HellBotException
from Music.utils.play import player

from .database import db

on_mode = ["on", "enable", "yes", "true"]


# check if private mode is enabled or not
def check_mode(func):
    @wraps(func)
    async def decorated(client, message):
        user_id = message.from_user.id
        if (Config.PRIVATE_MODE).lower in on_mode:
            if user_id not in Config.SUDO_USERS:
                return
        await func(client, message)

    return decorated


# allow admins only
def AdminWrapper(func):
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
        if message.from_user.id not in Config.SUDO_USERS:
            if not await get_user_rights(chat_id, message.from_user.id):
                return await message.reply_text(
                    "You don't have enough rights to use this command! You need to be an admin with manage voice chats permission to use this command."
                )
        return await func(client, message)

    return decorated


# allow admins and auth users only
def AuthWrapper(func):
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
        is_authchat = await db.is_authchat(message.chat.id)
        if not is_authchat:
            if message.from_user.id not in Config.SUDO_USERS:
                try:
                    admins = await get_auth_users(chat_id)
                except Exception as e:
                    raise HellBotException(f"[HellBotException]: {e}")
                if not admins:
                    return await message.reply_text(
                        "Need to refresh admin list. Click here -> /reload"
                    )
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(
                            "This command is only for authorized users and admins!"
                        )
        return await func(client, message)

    return decorated


# allow normal users only
def UserWrapper(func):
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
        return await func(client, message)

    return decorated


# wrapper to check and return context
def PlayWrapper(func):
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
        video = forceplay = False
        url = await player.get_url(message)
        if message.reply_to_message:
            tg_audio = (
                message.reply_to_message.audio or message.reply_to_message.voice or None
            )
            tg_video = (
                message.reply_to_message.video
                or message.reply_to_message.document
                or None
            )
        else:
            tg_audio = tg_video = None
        if not tg_audio and not tg_video and not url:
            if not len(message.command) >= 2:
                return await message.reply_text(
                    "Reply to an audio/video file or YouTube link to play it!"
                )
        if message.command[0][0] == "v":
            video = True
        elif message.command[0][0] == "f":
            forceplay = True
            if message.command[0][1] == "v":
                video = True
        if tg_video:
            video = True

        context = {
            "is_video": video,
            "is_force": forceplay,
            "is_url": url,
            "is_tgaudio": tg_audio,
            "is_tgvideo": tg_video,
        }
        return await func(client, message, context)

    return decorated
