from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from config import Config
from Music.core.calls import hellmusic
from Music.core.clients import hellbot
from Music.core.database import db
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.utils.admins import get_auth_users
from Music.utils.play import player
from Music.utils.queue import Queue
from Music.utils.youtube import ytube


@hellbot.app.on_callback_query(filters.regex(r"close") & ~Config.BANNED_USERS)
async def close_cb(_, cb: CallbackQuery):
    try:
        await cb.message.delete()
        await cb.answer("Closed!", show_alert=True)
    except:
        pass


@hellbot.app.on_callback_query(filters.regex(r"controls") & ~Config.BANNED_USERS)
async def controls_cb(_, cb: CallbackQuery):
    video_id = cb.data.split("|")[1]
    chat_id = int(cb.data.split("|")[2])
    btns = Buttons.controls_markup(video_id, chat_id)
    try:
        await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
    except:
        return


@hellbot.app.on_callback_query(filters.regex(r"player") & ~Config.BANNED_USERS)
async def player_cb(_, cb: CallbackQuery):
    _, video_id, chat_id = cb.data.split("|")
    btns = Buttons.player_markup(chat_id, video_id, hellbot.app.username)
    try:
        await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
    except:
        return


@hellbot.app.on_callback_query(filters.regex(r"ctrl") & ~Config.BANNED_USERS)
async def controler_cb(_, cb: CallbackQuery):
    _, action, chat_id = cb.data.split("|")
    if int(chat_id) != cb.message.chat.id:
        return await cb.answer("This message is not for this chat!", show_alert=True)
    is_active = await db.is_active_vc(int(chat_id))
    if not is_active:
        return await cb.answer("Voice chat is not active!", show_alert=True)
    is_authchat = await db.is_authchat(cb.message.chat.id)
    if not is_authchat:
        if cb.from_user.id not in Config.SUDO_USERS:
            try:
                admins = await get_auth_users(int(chat_id))
            except Exception as e:
                return await cb.answer(
                    f"There was an error while fetching admin list.\n\n{e}",
                    show_alert=True,
                )
            if not admins:
                return await cb.answer("Need to refresh admin list.", show_alert=True)
            else:
                if cb.from_user.id not in admins:
                    return await cb.answer(
                        "This command is only for authorized users and admins!",
                        show_alert=True,
                    )
    if action == "play":
        is_paused = await db.get_watcher(cb.message.chat.id, "pause")
        if is_paused:
            await db.set_watcher(cb.message.chat.id, "pause", False)
            await hellmusic.resume_vc(cb.message.chat.id)
            await cb.answer("Resumed!", show_alert=True)
            return await cb.message.reply_text(
                f"__VC Resumed by:__ {cb.from_user.mention}"
            )
        else:
            await db.set_watcher(cb.message.chat.id, "pause", True)
            await hellmusic.pause_vc(cb.message.chat.id)
            await cb.answer("Paused!", show_alert=True)
            return await cb.message.reply_text(
                f"__VC Paused by:__ {cb.from_user.mention}"
            )
    elif action == "mute":
        is_muted = await db.get_watcher(cb.message.chat.id, "mute")
        if is_muted:
            return await cb.answer("Already muted!", show_alert=True)
        else:
            await db.set_watcher(cb.message.chat.id, "mute", True)
            await hellmusic.mute_vc(cb.message.chat.id)
            await cb.answer("Muted!", show_alert=True)
            return await cb.message.reply_text(
                f"__VC Muted by:__ {cb.from_user.mention}"
            )
    elif action == "unmute":
        is_muted = await db.get_watcher(cb.message.chat.id, "mute")
        if is_muted:
            await db.set_watcher(cb.message.chat.id, "mute", False)
            await hellmusic.unmute_vc(cb.message.chat.id)
            await cb.answer("Unmuted!", show_alert=True)
            return await cb.message.reply_text(
                f"__VC Unmuted by:__ {cb.from_user.mention}"
            )
        else:
            return await cb.answer("Already unmuted!", show_alert=True)
    elif action == "end":
        await hellmusic.leave_vc(cb.message.chat.id)
        await db.set_loop(cb.message.chat.id, 0)
        await cb.answer("Left the VC!", show_alert=True)
        return await cb.message.reply_text(f"__VC Stopped by:__ {cb.from_user.mention}")
    elif action == "loop":
        is_loop = await db.get_loop(cb.message.chat.id)
        final = is_loop + 3
        final = 10 if final > 10 else final
        await db.set_loop(cb.message.chat.id, final)
        await cb.answer(f"Loop set to {final}", show_alert=True)
        return await cb.message.reply_text(
            f"__Loop set to {final}__ by: {cb.from_user.mention}\n\nPrevious loop was {is_loop}"
        )
    elif action == "replay":
        hell = await cb.message.reply_text("Processing ...")
        que = Queue.get_queue(cb.message.chat.id)
        if que == []:
            await hell.delete()
            return await cb.answer("No songs in queue to replay!", show_alert=True)
        await cb.answer("Replaying!", show_alert=True)
        await player.replay(cb.message.chat.id, hell)
    elif action == "skip":
        hell = await cb.message.reply_text("Processing ...")
        que = Queue.get_queue(cb.message.chat.id)
        if que == []:
            await hell.delete()
            return await cb.answer("No songs in queue to skip!", show_alert=True)
        if len(que) == 1:
            await hell.delete()
            return await cb.answer(
                "No more songs in queue to skip! Use /end or /stop to stop the VC.",
                show_alert=True,
            )
        is_loop = await db.get_loop(cb.message.chat.id)
        if is_loop != 0:
            await db.set_loop(cb.message.chat.id, 0)
        await player.skip(cb.message.chat.id, hell)
    elif action == "bseek":
        que = Queue.get_queue(cb.message.chat.id)
        if que == []:
            return await cb.answer("No songs in queue to seek!", show_alert=True)
        played = int(que[0]["played"])
        seek_time = 10
        if (played - seek_time) <= 10:
            return await cb.answer("Cannot seek beyond 10 seconds!", show_alert=True)
        to_seek = played - seek_time
        video = True if que[0]["vc_type"] == "video" else False
        if que[0]["file"] == que[0]["video_id"]:
            file_path = await ytube.download(que[0]["video_id"], True, video)
        else:
            file_path = que[0]["file"]
        try:
            context = {
                "chat_id": que[0]["chat_id"],
                "file": file_path,
                "duration": que[0]["duration"],
                "seek": formatter.secs_to_mins(to_seek),
                "video": video,
            }
            await hellmusic.seek_vc(context)
        except:
            return await cb.answer("Something went wrong!", show_alert=True)
        Queue.update_duration(cb.message.chat.id, 0, to_seek)
        await cb.message.reply_text(
            f"__Seeked back by {seek_time} seconds!__ \n\nBy: {cb.from_user.mention}"
        )
    elif action == "fseek":
        que = Queue.get_queue(cb.message.chat.id)
        if que == []:
            return await cb.answer("No songs in queue to seek!", show_alert=True)
        played = int(que[0]["played"])
        duration = formatter.mins_to_secs(que[0]["duration"])
        seek_time = 10
        if (duration - (played + seek_time)) <= 10:
            return await cb.answer("Cannot seek beyond 10 seconds!", show_alert=True)
        to_seek = played + seek_time
        try:
            context = {
                "chat_id": que[0]["chat_id"],
                "file": que[0]["file"],
                "duration": que[0]["duration"],
                "seek": formatter.secs_to_mins(to_seek),
                "video": True if que[0]["vc_type"] == "video" else False,
            }
            await hellmusic.seek_vc(context)
        except:
            return await cb.answer("Something went wrong!", show_alert=True)
        Queue.update_duration(cb.message.chat.id, 1, to_seek)
        await cb.message.reply_text(
            f"__Seeked forward by {seek_time} seconds!__ \n\nBy: {cb.from_user.mention}"
        )
    elif action == "back":
        que = Queue.get_queue(cb.message.chat.id)
        if que == []:
            video_id = "telegram"
        else:
            video_id = que[0]["video_id"]
        btns = Buttons.player_markup(cb.message.chat.id, video_id, hellbot.app.username)
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
        except:
            return


@hellbot.app.on_callback_query(filters.regex(r"help") & ~Config.BANNED_USERS)
async def help_cb(_, cb: CallbackQuery):
    data = cb.data.split("|")[1]
    if data == "admin":
        return await cb.message.edit_text(
            TEXTS.HELP_ADMIN, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "user":
        return await cb.message.edit_text(
            TEXTS.HELP_USER, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "sudo":
        return await cb.message.edit_text(
            TEXTS.HELP_SUDO, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "others":
        return await cb.message.edit_text(
            TEXTS.HELP_OTHERS, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "owner":
        return await cb.message.edit_text(
            TEXTS.HELP_OWNERS, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "back":
        return await cb.message.edit_text(
            TEXTS.HELP_PM.format(hellbot.app.mention),
            reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
        )
    elif data == "start":
        return await cb.message.edit_text(
            TEXTS.START_PM.format(
                cb.from_user.first_name,
                hellbot.app.mention,
                hellbot.app.username,
            ),
            reply_markup=InlineKeyboardMarkup(Buttons.start_pm_markup(hellbot.app.username)),
            disable_web_page_preview=True,
        )


@hellbot.app.on_callback_query(filters.regex(r"source") & ~Config.BANNED_USERS)
async def source_cb(_, cb: CallbackQuery):
    await cb.message.edit_text(
        TEXTS.SOURCE.format(hellbot.app.mention),
        reply_markup=InlineKeyboardMarkup(Buttons.source_markup()),
        disable_web_page_preview=True,
    )
