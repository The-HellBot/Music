from pyrogram.types import InlineKeyboardButton

from Music.core.clients import hellbot


class MakeButtons:
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

    def controls_markup(video_id, chat_id):
        buttons = [
            [
                InlineKeyboardButton(text="⟲", callback_data=f"authcontrols|bseek|{chat_id}"),
                InlineKeyboardButton(text="⦿", callback_data=f"authcontrols|play|{chat_id}"),
                InlineKeyboardButton(text="⟳", callback_data=f"authcontrols|fseek|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="⊡ End", callback_data=f"authcontrols|end|{chat_id}"),
                InlineKeyboardButton(text="↻ Replay", callback_data=f"authcontrols|replay|{chat_id}"),
                InlineKeyboardButton(text="∞ Loop", callback_data=f"authcontrols|loop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="⊝ Mute", callback_data=f"authcontrols|mute|{chat_id}"),
                InlineKeyboardButton(text="⊜ Unmute", callback_data=f"authcontrols|unmute|{chat_id}"),
                InlineKeyboardButton(text="⊹ Skip", callback_data=f"authcontrols|skip|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙", callback_data=f"controls|{chat_id}|{video_id}"),
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ]
        ]
        return buttons