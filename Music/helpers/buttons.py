from pyrogram.types import InlineKeyboardButton


class MakeButtons:
    def __init__(self):
        pass

    def close_markup(self):
        buttons = [[InlineKeyboardButton("🗑", callback_data="close")]]
        return buttons

    def queue_markup(self, count: int, page: int):
        if count != 1:
            buttons = [
                [
                    InlineKeyboardButton("⪨", callback_data=f"queue|prev|{page}"),
                    InlineKeyboardButton("🗑", callback_data="close"),
                    InlineKeyboardButton("⪩", callback_data=f"queue|next|{page}"),
                ]
            ]
        else:
            buttons = [
                [
                    InlineKeyboardButton("🗑", callback_data="close"),
                ]
            ]

        return buttons

    async def favorite_markup(
        self, collection: list, user_id: int, page: int, index: int, db, delete: bool
    ):
        btns = []
        txt = ""
        if len(collection) != 1:
            nav_btns = [
                [
                    InlineKeyboardButton("⪨", callback_data=f"myfavs|prev|{user_id}|{page}"),
                    InlineKeyboardButton("🗑", callback_data=f"myfavs|close|{user_id}|{page}"),
                    InlineKeyboardButton("⪩", callback_data=f"myfavs|next|{user_id}|{page}"),
                ]
            ]
        else:
            nav_btns = [
                [
                    InlineKeyboardButton("🗑", callback_data=f"myfavs|close|{user_id}|{page}"),
                ],
            ]
        try:
            for track in collection[page]:
                index += 1
                favs = await db.get_favorite(user_id, str(track))
                txt += f"**{'0' if index < 10 else ''}{index}:** {favs['title']}\n"
                txt += f"    **Duration:** {favs['duration']}\n"
                txt += f"    **Since:** {favs['add_date']}\n\n"
                btns.append(InlineKeyboardButton(text=f"{index}", callback_data=f"delfavs|{track}|{user_id}"))
        except:
            page = 0
            for track in collection[page]:
                index += 1
                favs = await db.get_favorite(user_id, track)
                txt += f"**{'0' if index < 10 else ''}{index}:** {favs['title']}\n"
                txt += f"    **Duration:** {favs['duration']}\n"
                txt += f"    **Since:** {favs['add_date']}\n\n"
                btns.append(InlineKeyboardButton(text=f"{index}", callback_data=f"delfavs|{track}|{user_id}"))

        if delete:
            btns.append(InlineKeyboardButton(text="Delete All ❌", callback_data=f"delfavs|all|{user_id}"))
            buttons = [btns] + nav_btns
        else:
            buttons = nav_btns

        return buttons, txt

    def active_vc_markup(self, count: int, page: int):
        if count != 1:
            buttons = [
                [
                    InlineKeyboardButton(text="⪨", callback_data=f"activevc|prev|{page}"),
                    InlineKeyboardButton(text="🗑", callback_data="close"),
                    InlineKeyboardButton(text="⪩", callback_data=f"activevc|next|{page}"),
                ]
            ]
        else:
            buttons = [[InlineKeyboardButton(text="🗑", callback_data="close")]]
        return buttons

    def authusers_markup(self, count: int, page: int, rand_key: str):
        if count != 1:
            buttons = [
                [
                    InlineKeyboardButton(text="⪨", callback_data=f"authus|prev|{page}|{rand_key}"),
                    InlineKeyboardButton(text="🗑", callback_data=f"authus|close|{page}|{rand_key}"),
                    InlineKeyboardButton(text="⪩", callback_data=f"authus|next|{page}|{rand_key}"),
                ]
            ]
        else:
            buttons = [
                [
                    InlineKeyboardButton(text="🗑", callback_data=f"authus|close|{page}|{rand_key}")
                ]
            ]
        return buttons

    def player_markup(self, chat_id, video_id, username):
        if video_id == "telegram":
            buttons = [
                [
                    InlineKeyboardButton("🎛️", callback_data=f"controls|{video_id}|{chat_id}"),
                    InlineKeyboardButton("🗑", callback_data="close"),
                ]
            ]
        else:
            buttons = [
                [
                    InlineKeyboardButton("About Song", url=f"https://t.me/{username}?start=song_{video_id}"),
                ],
                [
                    InlineKeyboardButton("❤️", callback_data=f"add_favorite|{video_id}"),
                    InlineKeyboardButton("🎛️", callback_data=f"controls|{video_id}|{chat_id}"),
                ],
                [
                    InlineKeyboardButton("🗑", callback_data="close"),
                ],
            ]
        return buttons

    def controls_markup(self, video_id, chat_id):
        buttons = [
            [
                InlineKeyboardButton(text="⟲", callback_data=f"ctrl|bseek|{chat_id}"),
                InlineKeyboardButton(text="⦿", callback_data=f"ctrl|play|{chat_id}"),
                InlineKeyboardButton(text="⟳", callback_data=f"ctrl|fseek|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="⊡ End", callback_data=f"ctrl|end|{chat_id}"),
                InlineKeyboardButton(text="↻ Replay", callback_data=f"ctrl|replay|{chat_id}"),
                InlineKeyboardButton(text="∞ Loop", callback_data=f"ctrl|loop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="⊝ Mute", callback_data=f"ctrl|mute|{chat_id}"),
                InlineKeyboardButton(text="⊜ Unmute", callback_data=f"ctrl|unmute|{chat_id}"),
                InlineKeyboardButton(text="⊹ Skip", callback_data=f"ctrl|skip|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙", callback_data=f"player|{video_id}|{chat_id}"),
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ],
        ]
        return buttons

    def song_markup(self, rand_key, url, key):
        buttons = [
            [
                InlineKeyboardButton(text="Visit Youtube", url=url),
            ],
            [
                InlineKeyboardButton(text="Audio", callback_data=f"song_dl|adl|{key}|{rand_key}"),
                InlineKeyboardButton(text="Video", callback_data=f"song_dl|vdl|{key}|{rand_key}"),
            ],
            [
                InlineKeyboardButton(text="⪨", callback_data=f"song_dl|prev|{key}|{rand_key}"),
                InlineKeyboardButton(text="⪩", callback_data=f"song_dl|next|{key}|{rand_key}"),
            ],
            [
                InlineKeyboardButton(text="🗑", callback_data=f"song_dl|close|{key}|{rand_key}"),
            ],
        ]

        return buttons

    def song_details_markup(self, url, ch_url):
        buttons = [
            [
                InlineKeyboardButton(text="🎥", url=url),
                InlineKeyboardButton(text="📺", url=ch_url),
            ],
            [
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ],
        ]
        return buttons

    def start_markup(self, username: str):
        buttons = [
            [
                InlineKeyboardButton(text="Start Me 🎵", url=f"https://t.me/{username}?start=start"),
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ]
        ]
        return buttons

    def help_gc_markup(self, username: str):
        buttons = [
            [
                InlineKeyboardButton(text="Get Help ❓", url=f"https://t.me/{username}?start=help"),
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ]
        ]
        return buttons

    def help_pm_markup(self):
        buttons = [
            [
                InlineKeyboardButton(text="➊ Admins", callback_data="help|admin"),
                InlineKeyboardButton(text="➋ Users", callback_data="help|user"),
            ],
            [
                InlineKeyboardButton(text="➌ Sudos", callback_data="help|sudo"),
                InlineKeyboardButton(text="➍ Others", callback_data="help|others"),
            ],
            [
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ],
        ]
        return buttons

    def help_back(self):
        buttons = [
            [
                InlineKeyboardButton(text="🔙", callback_data="help|back"),
                InlineKeyboardButton(text="🗑", callback_data="close"),
            ]
        ]
        return buttons


Buttons = MakeButtons()
