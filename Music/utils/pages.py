from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message

from config import Config
from Music.core import hellbot
from Music.helpers.formatters import formatter
from Music.helpers.buttons import Buttons


class MakePages:
    async def song_page(message, rand_key, key):
        m = message.message if isinstance(message, CallbackQuery) else message
        if Config.SONG_CACHE[rand_key]:
            all_tracks = Config.SONG_CACHE[rand_key]
            btns = Buttons.song_markup(rand_key, all_tracks[key]["full_link"], key)
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

    async def activevc_page(
        message: Message or CallbackQuery,
        collection: list,
        page: int = 0,
        index: int = 0,
        edit: bool = False,
    ):
        m = message.message if isinstance(message, CallbackQuery) else message
        grouped, total = formatter.group_the_list(collection)
        text = f"__({page+1}/{len(grouped)})__ **{hellbot.app.mention} Active Voice Chats:** __{total} chats__\n\n"
        btns = Buttons.active_vc_markup(len(grouped), page)
        try:
            for active in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {active['title']} [`{active['chat_id']}`]\n"
                text += f"    **Listeners:** __{active['participants']}__\n"
                text += f"    **Playing:** __{active['playing']}__\n"
                text += f"    **Since:** __{active['active_since']}__\n\n"
        except IndexError:
            page = 0
            for active in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {active['title']} [`{active['chat_id']}`]\n"
                text += f"    **Listeners:** __{active['participants']}__\n"
                text += f"    **Playing:** __{active['playing']}__\n"
                text += f"    **Since:** __{active['active_since']}__\n\n"
        if edit:
            await m.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
        else:
            await m.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))
