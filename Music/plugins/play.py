import asyncio
import random

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from config import Config
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.decorators import AuthWrapper, PlayWrapper, UserWrapper, check_mode
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.utils.pages import MakePages
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
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, user_name)
    else:
        try:
            await db.update_user(user_id, "user_name", user_name)
        except:
            pass
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
        time_check = formatter.check_limit(tgvid.duration, play_limit)
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
            await hell.edit("Processing the playlist ...")
            song_list = await ytube.get_playlist(url)
            random.shuffle(song_list)
            context = {
                "user_id": message.from_user.id,
                "user_mention": message.from_user.mention,
            }
            await player.playlist(hell, context, song_list, video)
            return
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


@hellbot.app.on_message(
    filters.command(["current", "playing"]) & filters.group & ~Config.BANNED_USERS
)
@UserWrapper
async def playing(_, message: Message):
    chat_id = message.chat.id
    is_active = await db.is_active_vc(chat_id)
    if not is_active:
        return await message.reply_text("No active voice chat found here.")
    que = Queue.get_current(chat_id)
    if not que:
        return await message.reply_text("Nothing is playing here.")
    photo = thumb.generate((359), (297, 302), que["video_id"])
    btns = Buttons.player_markup(chat_id, que["video_id"], hellbot.app.username)
    to_send = TEXTS.PLAYING.format(
        hellbot.app.mention,
        que["title"],
        que["duration"],
        que["user"],
    )
    if photo:
        sent = await message.reply_photo(
            photo, caption=to_send, reply_markup=InlineKeyboardMarkup(btns)
        )
    else:
        sent = await message.reply_text(
            to_send, reply_markup=InlineKeyboardMarkup(btns)
        )
    previous = Config.PLAYER_CACHE.get(chat_id)
    if previous:
        try:
            await previous.delete()
        except Exception:
            pass
    Config.PLAYER_CACHE[chat_id] = sent


@hellbot.app.on_message(
    filters.command(["queue", "que", "q"]) & filters.group & ~Config.BANNED_USERS
)
@UserWrapper
async def queued_tracks(_, message: Message):
    hell = await message.reply_text("Getting Queue...")
    chat_id = message.chat.id
    is_active = await db.is_active_vc(chat_id)
    if not is_active:
        return await hell.edit_text("No active voice chat found here.")
    collection = Queue.get_queue(chat_id)
    if not collection:
        return await hell.edit_text("Nothing is playing here.")
    await MakePages.queue_page(hell, collection, 0, 0, True)


@hellbot.app.on_message(filters.command(["clean", "reload"]) & ~Config.BANNED_USERS)
@AuthWrapper
async def clean_queue(_, message: Message):
    Queue.clear_queue(message.chat.id)
    hell = await message.reply_text("**Cleared Queue.**")
    await asyncio.sleep(10)
    await hell.delete()


@hellbot.app.on_callback_query(filters.regex(r"queue") & ~Config.BANNED_USERS)
async def queued_tracks_cb(_, cb: CallbackQuery):
    _, action, page = cb.data.split("|")
    key = int(page)
    collection = Queue.get_queue(cb.message.chat.id)
    length, _ = formatter.group_the_list(collection, 5, True)
    length -= 1
    if key == 0 and action == "prev":
        new_page = length
    elif key == length and action == "next":
        new_page = 0
    else:
        new_page = key + 1 if action == "next" else key - 1
    index = new_page * 5
    await MakePages.queue_page(cb.message, collection, new_page, index, True)
