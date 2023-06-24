from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto

from config import Config
from Music.core import hellbot
from Music.helpers.buttons import MakeButtons


class MakePages:
    async def song_page(message, rand_key, key):
        m = message.message if isinstance(message, CallbackQuery) else message
        if Config.SONG_CACHE[rand_key]:
            all_tracks = Config.SONG_CACHE[rand_key]
            btns = MakeButtons.song_markup(rand_key, all_tracks[key]["full_link"], key)
            cap = f"**{hellbot.app.mention} Song Downloader:**\n"
            cap += f"**Page:** `{key+1} / {len(all_tracks)}\n\n"
            cap += f"**• Title:** `{all_tracks[key]['title']}`\n"
            await m.edit_media(
                InputMediaPhoto(
                    all_tracks[key]["thumb"],
                    caption=cap,
                ),
                reply_markup=InlineKeyboardMarkup(btns),
            )
        else:
            await m.delete()
            return await m.reply_text("Query timed out! Please start the query again.")
