from pyrogram import filters
from pyrogram.types import Message

from config import Config
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.decorators import PlayWrapper, check_mode, UserWrapper
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.utils.play import player
from Music.utils.queue import Queue
from Music.utils.thumbnail import thumb
from Music.utils.youtube import ytube


@hellbot.app.on_message(
    filters.command(["play", "vplay", "fplay", "fvplay"])
    & filters.group
    & ~Config.BANNED_USERS
)
@check_mode
@PlayWrapper
async def play_music(_, message: Message, context: dict):
    hell = await message.reply_text("Processing ...")
    # initialise variables
    video, force, url, tgaud, tgvid = context.values()
    play_limit = formatter.mins_to_secs(f"{Config.PLAY_LIMIT}:00")

    # if the user replied to a message and that message is an audio file
    if tgaud:
        size_check = formatter.check_limit(tgaud.file_size, Config.TG_AUDIO_SIZE_LIMIT)
        if not size_check:
            return await hell.edit(
                f"Audio file size exceeds the size limit of {formatter.bytes_to_mb(Config.TG_AUDIO_SIZE_LIMIT)}MB."
            )
        time_check = formatter.check_limit(tgaud.duration, play_limit)
        if not time_check:
            return await hell.edit(
                f"Audio duration limit of {Config.PLAY_LIMIT} minutes exceeded."
            )
        await hell.edit("Downloading ...")
        file_path = await hellbot.app.download_media(message.reply_to_message)
        context = {
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "duration": formatter.secs_to_mins(tgaud.duration),
            "file": file_path,
            "title": "Telegram Audio",
            "user": message.from_user.mention,
            "video_id": "telegram",
            "vc_type": "voice",
            "force": force,
        }
        await player.play(hell, context)
        return

    # if the user replied to a message and that message is a video file
    if tgvid:
        size_check = formatter.check_limit(tgvid.file_size, Config.TG_VIDEO_SIZE_LIMIT)
        if not size_check:
            return await hell.edit(
                f"Video file size exceeds the size limit of {formatter.bytes_to_mb(Config.TG_VIDEO_SIZE_LIMIT)}MB."
            )
        time_check = formatter.check_limit(tgaud.duration, play_limit)
        if not time_check:
            return await hell.edit(
                f"Audio duration limit of {Config.PLAY_LIMIT} minutes exceeded."
            )
        await hell.edit("Downloading ...")
        file_path = await hellbot.app.download_media(message.reply_to_message)
        context = {
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "duration": formatter.secs_to_mins(tgvid.duration),
            "file": file_path,
            "title": "Telegram Video",
            "user": message.from_user.mention,
            "video_id": "telegram",
            "vc_type": "video",
            "force": force,
        }
        await player.play(hell, context)
        return

    # if the user replied to or sent a youtube link
    if url:
        if not ytube.check(url):
            return await hell.edit("Invalid YouTube URL.")
        if "playlist" in url:
            return await hell.edit("Playlist links are not supported yet.")
        try:
            await hell.edit("Searching ...")
            result = await ytube.get_data(url, False)
        except Exception as e:
            return await hell.edit(f"**Error:**\n`{e}`")
        context = {
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "duration": result[0]["duration"],
            "file": result[0]["id"],
            "title": result[0]["title"],
            "user": message.from_user.mention,
            "video_id": result[0]["id"],
            "vc_type": "video" if video else "voice",
            "force": force,
        }
        await player.play(hell, context)
        return

    # if the user sent a query
    query = message.text.split(" ", 1)[1]
    try:
        await hell.edit("Searching ...")
        result = await ytube.get_data(query, False)
    except Exception as e:
        return await hell.edit(f"**Error:**\n`{e}`")
    context = {
        "chat_id": message.chat.id,
        "user_id": message.from_user.id,
        "duration": result[0]["duration"],
        "file": result[0]["id"],
        "title": result[0]["title"],
        "user": message.from_user.mention,
        "video_id": result[0]["id"],
        "vc_type": "video" if video else "voice",
        "force": force,
    }
    await player.play(hell, context)


@hellbot.app.on_message(filters.command(["current", "playing"]) & filters.group & ~Config.BANNED_USERS)
@UserWrapper
async def playing(_, message: Message):
    chat_id = message.chat.id
    is_active = await db.is_active_vc(chat_id)
    if not is_active:
        return await message.reply_text("No active voice chat found here.")
    que = Queue.get_current(chat_id)
    if not que:
        return await message.reply_text("Nothing is playing here.")
    to_send = TEXTS.PLAYING.format(
        hellbot.app.mention,
        que["title"],
        que["duration"],
        que["user"],
    )
    photo = thumb.generate((359), (297, 302), que["video_id"])
    btns = Buttons.player_markup(chat_id, que["video_id"], hellbot.app.mention)
    if photo:
        await message.reply_photo(photo, caption=to_send)
    else:
        await message.reply_text(to_send)
