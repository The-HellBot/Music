import os

from pyrogram.enums import MessageEntityType
from pyrogram.types import InlineKeyboardMarkup, Message

from config import Config
from Music.core.calls import hellmusic
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.helpers.buttons import Buttons
from Music.helpers.strings import TEXTS

from .queue import Queue
from .thumbnail import thumb
from .youtube import ytube


class Player:
    def __init__(self) -> None:
        pass

    async def get_url(self, message: Message):
        msg = [message]
        if message.reply_to_message:
            msg.append(message.reply_to_message)
        url = ""
        offset = length = None
        for m in msg:
            if offset:
                break
            if m.entities:
                for entity in m.entities:
                    if entity.type == MessageEntityType.URL:
                        url = m.text or m.caption
                        offset, length = entity.offset, entity.length
                        break
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
            elif m.caption_entities:
                for entity in m.caption_entities:
                    if entity.type == MessageEntityType.URL:
                        url = m.text or m.caption
                        offset, length = entity.offset, entity.length
                        break
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return url[offset : offset + length]

    async def play(self, message: Message, context: dict, edit: bool = True):
        (
            chat_id,
            user_id,
            duration,
            file,
            title,
            user,
            video_id,
            vc_type,
            force,
        ) = context.values()
        if force:
            await hellmusic.leave_vc(chat_id, True)
        if video_id == "telegram":
            file_path = file
        else:
            try:
                if edit:
                    await message.edit_text("Downloading ...")
                else:
                    await message.reply_text("Downloading ...")
                file_path = await ytube.download(
                    video_id, True, True if vc_type == "video" else False
                )
            except Exception as e:
                if edit:
                    await message.edit_text(str(e))
                else:
                    await message.reply_text(str(e))
                return
        position = Queue.put_queue(
            chat_id,
            user_id,
            duration,
            file_path,
            title,
            user,
            video_id,
            vc_type,
            force,
        )
        if position == 0:
            photo = thumb.generate((359), (297, 302), video_id)
            try:
                await hellmusic.join_vc(
                    chat_id, file_path, True if vc_type == "video" else False
                )
            except Exception as e:
                await message.delete()
                await message.reply_text(str(e))
                Queue.clear_queue(chat_id)
                os.remove(file_path)
                os.remove(photo)
                return
            btns = Buttons.player_markup(chat_id, video_id, hellbot.app.username)
            if photo:
                sent = await hellbot.app.send_photo(
                    chat_id,
                    photo,
                    TEXTS.PLAYING.format(
                        hellbot.app.mention,
                        title,
                        duration,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(btns),
                )
                os.remove(photo)
            else:
                sent = await hellbot.app.send_message(
                    chat_id,
                    TEXTS.PLAYING.format(
                        hellbot.app.mention,
                        title,
                        duration,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(btns),
                )
            previous = Config.PLAYER_CACHE.get(chat_id)
            if previous:
                try:
                    await previous.delete()
                except Exception:
                    pass
            Config.PLAYER_CACHE[chat_id] = sent
        else:
            sent = await hellbot.app.send_message(
                chat_id,
                TEXTS.QUEUE.format(
                    position,
                    title,
                    duration,
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
            )
            prev_q = Config.QUEUE_CACHE.get(chat_id)
            if prev_q:
                try:
                    await prev_q.delete()
                except Exception:
                    pass
            Config.QUEUE_CACHE[chat_id] = sent
            return await message.delete()
        await message.delete()
        await db.update_songs_count(1)
        await db.update_user(user_id, "songs_played", 1)
        chat_name = (await hellbot.app.get_chat(chat_id)).title
        await hellbot.logit(
            f"play {vc_type}",
            f"**⤷ Song:** `{title}` \n**⤷ Chat:** {chat_name} [`{chat_id}`] \n**⤷ User:** {user}",
        )

    async def skip(self, chat_id: int, message: Message):
        await message.edit_text("Skipping ...")
        await hellmusic.change_vc(chat_id)
        await message.delete()

    async def replay(self, chat_id: int, message: Message):
        que = Queue.get_current(chat_id)
        if not que:
            return await message.edit_text("Nothing is playing to replay")
        video = True if que["vc_type"] == "video" else False
        photo = thumb.generate((359), (297, 302), que["video_id"])
        if que["file"] == que["video_id"]:
            file_path = await ytube.download(que["video_id"], True, video)
        else:
            file_path = que["file"]
        try:
            await hellmusic.replay_vc(chat_id, file_path, video)
        except Exception as e:
            await message.delete()
            await message.reply_text(str(e))
            Queue.clear_queue(chat_id)
            os.remove(que["file"])
            os.remove(photo)
            return
        btns = Buttons.player_markup(chat_id, que["video_id"], hellbot.app.username)
        if photo:
            sent = await hellbot.app.send_photo(
                chat_id,
                photo,
                TEXTS.PLAYING.format(
                    hellbot.app.mention,
                    que["title"],
                    que["duration"],
                    que["user"],
                ),
                reply_markup=InlineKeyboardMarkup(btns),
            )
            os.remove(photo)
        else:
            sent = await hellbot.app.send_message(
                chat_id,
                TEXTS.PLAYING.format(
                    hellbot.app.mention,
                    que["title"],
                    que["duration"],
                    que["user"],
                ),
                reply_markup=InlineKeyboardMarkup(btns),
            )
        previous = Config.PLAYER_CACHE.get(chat_id)
        if previous:
            try:
                await previous.delete()
            except Exception:
                pass
        Config.PLAYER_CACHE[chat_id] = sent
        await message.delete()

    async def playlist(
        self, message: Message, user_id: int, collection: list, video: bool = False
    ):
        hell = await message.edit_text("Playing your favorites ...")
        vc_type = "video" if video else "voice"
        count = failed = 0
        if await db.is_active_vc(message.chat.id):
            await hell.edit_text(
                "This chat have an active vc. Adding your favorites in the queue... \n\n__This might take some time!__"
            )
        previously = len(Queue.get_queue(message.chat.id))
        for i in collection:
            try:
                data = (await ytube.get_data(i, True, 1))[0]
                if count == 0 and previously == 0:
                    LOGS.info("Playing first song")
                    file_path = await ytube.download(data["id"], True, video)
                    _queue = Queue.put_queue(
                        message.chat.id,
                        user_id,
                        data["duration"],
                        file_path,
                        data["title"],
                        message.from_user.mention,
                        data["id"],
                        vc_type,
                        False,
                    )
                    try:
                        photo = thumb.generate((359), (297, 302), data["id"])
                        await hellmusic.join_vc(message.chat.id, file_path, video)
                    except Exception as e:
                        await hell.edit_text(str(e))
                        Queue.clear_queue(message.chat.id)
                        os.remove(file_path)
                        os.remove(photo)
                        return
                    btns = Buttons.player_markup(
                        message.chat.id, data["id"], hellbot.app.username
                    )
                    if photo:
                        sent = await hellbot.app.send_photo(
                            message.chat.id,
                            photo,
                            TEXTS.PLAYING.format(
                                hellbot.app.mention,
                                data["title"],
                                data["duration"],
                                message.from_user.mention,
                            ),
                            reply_markup=InlineKeyboardMarkup(btns),
                        )
                        os.remove(photo)
                    else:
                        sent = await hellbot.app.send_message(
                            message.chat.id,
                            TEXTS.PLAYING.format(
                                hellbot.app.mention,
                                data["title"],
                                data["duration"],
                                message.from_user.mention,
                            ),
                            reply_markup=InlineKeyboardMarkup(btns),
                        )
                    old = Config.PLAYER_CACHE.get(message.chat.id)
                    if old:
                        try:
                            await old.delete()
                        except Exception:
                            pass
                    Config.PLAYER_CACHE[message.chat.id] = sent
                else:
                    _queue = Queue.put_queue(
                        message.chat.id,
                        user_id,
                        data["duration"],
                        data["id"],
                        data["title"],
                        message.from_user.mention,
                        data["id"],
                        vc_type,
                        False,
                    )
                count += 1
            except Exception as e:
                LOGS.error(str(e))
                failed += 1
        await hell.edit_text(
            f"**Added all tracks to queue!** \n\n**Total tracks: `{count}`** \n**Failed: `{failed}`**"
        )


player = Player()
