from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from config import Config
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.decorators import UserWrapper, check_mode
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.users import MusicUser
from Music.utils.admins import get_user_type
from Music.utils.leaderboard import leaders


@hellbot.app.on_message(
    filters.command(["me", "profile"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@UserWrapper
async def user_profile(_, message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return await message.reply_text(
            "You are not yet registered on my database. Click on button below to register yourself.",
            reply_markup=InlineKeyboardMarkup(
                Buttons.start_markup(hellbot.app.username)
            ),
        )
    context = {
        "id": message.from_user.id,
        "mention": message.from_user.mention,
        "songs_played": user["songs_played"],
        "join_date": user["join_date"],
        "user_type": await get_user_type(message.chat.id, message.from_user.id),
    }
    await message.reply_text(
        MusicUser.get_profile_text(context, hellbot.app.mention),
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


@hellbot.app.on_message(filters.command("stats") & Config.SUDO_USERS)
@UserWrapper
async def stats(_, message: Message):
    hell = await message.reply_text("Just a sec... fetching stats")
    users = await db.total_users_count()
    chats = await db.total_chats_count()
    gbans = await db.total_gbans_count()
    block = await db.total_block_count()
    songs = await db.total_songs_count()
    actvc = await db.total_actvc_count()
    stats = await formatter.system_stats()
    context = {
        1: users,
        2: chats,
        3: gbans,
        4: block,
        5: songs,
        6: actvc,
        7: stats["core"],
        8: stats["cpu"],
        9: stats["disk"],
        10: stats["ram"],
        11: stats["uptime"],
        12: hellbot.app.mention,
    }
    await hell.edit_text(
        MusicUser.get_stats_text(context),
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


@hellbot.app.on_message(
    filters.command(["leaderboard", "topusers"]) & filters.group & ~Config.BANNED_USERS
)
@UserWrapper
async def topusers(_, message: Message):
    hell = await message.reply_text("Just a sec... fetching top users")
    context = {
        "mention": hellbot.app.mention,
        "username": hellbot.app.username,
        "client": hellbot.app,
    }
    text = await leaders.generate(context)
    btns = Buttons.close_markup()
    await hell.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(btns),
    )
