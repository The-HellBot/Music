from pyrogram import filters
from pyrogram.types import Message

from config import Config
from Music.core.clients import hellbot
from Music.core.decorators import PlayWrapper, check_mode
from Music.helpers.formatters import formatter
from Music.utils.play import player
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
        file_path = await tgaud.download()
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
        file_path = await tgvid.download()
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
            "duration": result["duration"],
            "file": result["id"],
            "title": result["title"],
            "user": message.from_user.mention,
            "video_id": result["id"],
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
        "duration": result["duration"],
        "file": result["id"],
        "title": result["title"],
        "user": message.from_user.mention,
        "video_id": result["id"],
        "vc_type": "video" if video else "voice",
        "force": force,
    }
    await player.play(hell, context)
