import datetime

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

from config import Config
from Music.core.calls import hellmusic
from Music.core.clients import hellbot
from Music.core.decorators import UserWrapper, check_mode
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.utils.youtube import ytube


@hellbot.app.on_message(filters.command(["start", "alive"]) & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def start(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) > 1:
            deep_cmd = message.text.split(None, 1)[1]
            if deep_cmd.startswith("song"):
                results = await ytube.get_data(deep_cmd.split("_", 1)[1], True)
                about = TEXTS.ABOUT_SONG.format(
                    results["title"],
                    results["channel"],
                    results["published"],
                    results["views"],
                    results["duration"],
                    hellbot.app.mention,
                )
                await message.reply_photo(
                    results["thumbnail"],
                    caption=about,
                    reply_markup=InlineKeyboardMarkup(
                        Buttons.song_details_markup(
                            results["link"],
                            results["ch_link"],
                        )
                    ),
                )
                return
            elif deep_cmd.startswith("help"):
                await message.reply_text(
                    TEXTS.HELP_PM.format(hellbot.app.mention),
                    reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
                )
                return
        await message.reply_text(TEXTS.START_PM.format(hellbot.app.mention))
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(TEXTS.START_GC)


@hellbot.app.on_message(filters.command("help") & ~Config.BANNED_USERS)
@UserWrapper
async def help(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            TEXTS.HELP_PM.format(hellbot.app.mention),
            reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
        )
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(
            TEXTS.HELP_GC,
            reply_markup=InlineKeyboardMarkup(Buttons.help_gc_markup(hellbot.app.username)),
        )


@hellbot.app.on_message(filters.command("ping") & ~Config.BANNED_USERS)
@UserWrapper
async def ping(_, message: Message):
    start_time = datetime.datetime.now()
    calls_ping = await hellmusic.ping()
    stats = await formatter.system_stats()
    end_time = (datetime.datetime.now() - start_time).microseconds / 1000
    await message.reply_text(
        TEXTS.PING_REPLY.format(end_time, stats["uptime"], calls_ping),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


@hellbot.app.on_message(filters.command("sysinfo") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def sysinfo(_, message: Message):
    stats = await formatter.system_stats()
    await message.reply_text(
        TEXTS.SYSTEM.format(
            stats["core"],
            stats["cpu"],
            stats["disk"],
            stats["ram"],
            stats["uptime"],
            hellbot.app.mention,
        ),
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )
