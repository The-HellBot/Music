from pyrogram.types import InlineKeyboardButton

from Music.core.clients import hellbot


def player_markup(chat_id, video_id):
    buttons = [
        [
            InlineKeyboardButton("About Song", url=f"https://t.me/{hellbot.app.username}?start=song_{video_id}"),
        ],
        [
            InlineKeyboardButton("❤️", callback_data=f"add_favorite|{video_id}"),
            InlineKeyboardButton("🎛️", callback_data=f"controls|{chat_id}|{video_id}"),
        ],
        [
            InlineKeyboardButton("🗑", callback_data="close"),
        ],
    ]
    return buttons
