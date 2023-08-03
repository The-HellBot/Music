import datetime
import os

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import MediumQualityAudio, MediumQualityVideo

from config import Config
from Music.helpers.buttons import Buttons
from Music.helpers.strings import TEXTS
from Music.utils.exceptions import (
    ChangeVCException,
    JoinGCException,
    JoinVCException,
    UserException,
)
from Music.utils.queue import Queue
from Music.utils.thumbnail import thumb
from Music.utils.youtube import ytube

from .clients import hellbot
from .database import db
from .logger import LOGS


async def __clean__(chat_id: int, force: bool):
    if force:
        Queue.rm_queue(chat_id, 0)
    else:
        Queue.clear_queue(chat_id)
    await db.remove_active_vc(chat_id)


class HellMusic(PyTgCalls):
    def __init__(self):
        self.music = PyTgCalls(hellbot.user)
        self.audience = {}

    async def autoend(self, chat_id: int, users: list):
        autoend = await db.get_autoend()
        if autoend:
            if len(users) == 1:
                get = await hellbot.app.get_users(users[0])
                if get.id == hellbot.user.id:
                    db.inactive[chat_id] = datetime.datetime.now() + datetime.timedelta(
                        minutes=5
                    )
            else:
                db.inactive[chat_id] = {}

    async def autoclean(self, file: str):
        # dirty way. but works :)
        try:
            os.remove(file)
            os.remove(f"downloads/{file}.webm")
            os.remove(f"downloads/{file}.mp4")
        except:
            pass

    async def start(self):
        LOGS.info(
            "\x3e\x3e\x20\x42\x6f\x6f\x74\x69\x6e\x67\x20\x50\x79\x54\x67\x43\x61\x6c\x6c\x73\x20\x43\x6c\x69\x65\x6e\x74\x2e\x2e\x2e"
        )
        if Config.HELLBOT_SESSION:
            await self.music.start()
            LOGS.info(
                "\x3e\x3e\x20\x42\x6f\x6f\x74\x65\x64\x20\x50\x79\x54\x67\x43\x61\x6c\x6c\x73\x20\x43\x6c\x69\x65\x6e\x74\x21"
            )
        else:
            LOGS.error(
                "\x3e\x3e\x20\x50\x79\x54\x67\x43\x61\x6c\x6c\x73\x20\x43\x6c\x69\x65\x6e\x74\x20\x6e\x6f\x74\x20\x62\x6f\x6f\x74\x65\x64\x21"
            )
            quit(1)

    async def ping(self):
        pinged = await self.music.ping
        return pinged

    async def vc_participants(self, chat_id: int):
        users = await self.music.get_participants(chat_id)
        return users

    async def mute_vc(self, chat_id: int):
        await self.music.mute_stream(chat_id)

    async def unmute_vc(self, chat_id: int):
        await self.music.unmute_stream(chat_id)

    async def pause_vc(self, chat_id: int):
        await self.music.pause_stream(chat_id)

    async def resume_vc(self, chat_id: int):
        await self.music.resume_stream(chat_id)

    async def leave_vc(self, chat_id: int, force: bool = False):
        try:
            await __clean__(chat_id, force)
            await self.music.leave_group_call(chat_id)
        except:
            pass
        previous = Config.PLAYER_CACHE.get(chat_id)
        if previous:
            try:
                await previous.delete()
            except:
                pass

    async def seek_vc(self, context: dict):
        chat_id, file_path, duration, to_seek, video = context.values()
        if video:
            input_stream = AudioVideoPiped(
                file_path,
                MediumQualityAudio(),
                MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        else:
            input_stream = AudioPiped(
                file_path,
                MediumQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        await self.music.change_stream(chat_id, input_stream)

    async def invited_vc(self, chat_id: int):
        try:
            await hellbot.app.send_message(
                chat_id, "The Bot will join vc only when you give something to play!"
            )
        except:
            return

    async def replay_vc(self, chat_id: int, file_path: str, video: bool = False):
        if video:
            input_stream = AudioVideoPiped(
                file_path, MediumQualityAudio(), MediumQualityVideo()
            )
        else:
            input_stream = AudioPiped(file_path, MediumQualityAudio())
        await self.music.change_stream(chat_id, input_stream)

    async def change_vc(self, chat_id: int):
        try:
            get = Queue.get_queue(chat_id)
            if get == []:
                return await self.leave_vc(chat_id)
            loop = await db.get_loop(chat_id)
            if loop == 0:
                file = Queue.rm_queue(chat_id, 0)
                await self.autoclean(file)
            else:
                await db.set_loop(chat_id, loop - 1)
        except Exception as e:
            LOGS.error(e)
            return await self.leave_vc(chat_id)
        get = Queue.get_queue(chat_id)
        if get == []:
            return await self.leave_vc(chat_id)
        chat_id = get[0]["chat_id"]
        duration = get[0]["duration"]
        queue = get[0]["file"]
        title = get[0]["title"]
        user_id = get[0]["user_id"]
        vc_type = get[0]["vc_type"]
        video_id = get[0]["video_id"]
        try:
            user = (await hellbot.app.get_users(user_id)).mention(style="md")
        except:
            user = get[0]["user"]
        if queue:
            tg = True if video_id == "telegram" else False
            if tg:
                to_stream = queue
            else:
                to_stream = await ytube.download(
                    video_id, True, True if vc_type == "video" else False
                )
            if vc_type == "video":
                input_stream = AudioVideoPiped(
                    to_stream, MediumQualityAudio(), MediumQualityVideo()
                )
            else:
                input_stream = AudioPiped(to_stream, MediumQualityAudio())
            try:
                photo = thumb.generate((359), (297, 302), video_id)
                await self.music.change_stream(int(chat_id), input_stream)
                btns = Buttons.player_markup(
                    chat_id,
                    "None" if video_id == "telegram" else video_id,
                    hellbot.app.username,
                )
                if photo:
                    sent = await hellbot.app.send_photo(
                        int(chat_id),
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
                        int(chat_id),
                        TEXTS.PLAYING.format(
                            hellbot.app.mention,
                            title,
                            duration,
                            user,
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(btns),
                    )
                previous = Config.PLAYER_CACHE.get(chat_id)
                if previous:
                    try:
                        await previous.delete()
                    except:
                        pass
                Config.PLAYER_CACHE[chat_id] = sent
                await db.update_songs_count(1)
                await db.update_user(user_id, "songs_played", 1)
                chat_name = (await hellbot.app.get_chat(chat_id)).title
                await hellbot.logit(
                    f"play {vc_type}",
                    f"**⤷ Song:** `{title}` \n**⤷ Chat:** {chat_name} [`{chat_id}`] \n**⤷ User:** {user}",
                )
            except Exception as e:
                raise ChangeVCException(f"[ChangeVCException]: {e}")

    async def join_vc(self, chat_id: int, file_path: str, video: bool = False):
        # define input stream
        if video:
            input_stream = AudioVideoPiped(
                file_path, MediumQualityAudio(), MediumQualityVideo()
            )
        else:
            input_stream = AudioPiped(file_path, MediumQualityAudio())

        # join vc
        try:
            await self.music.join_group_call(
                chat_id, input_stream, stream_type=StreamType().pulse_stream
            )
        except NoActiveGroupCall:
            try:
                await self.join_gc(chat_id)
            except Exception as e:
                await self.leave_vc(chat_id)
                raise JoinGCException(e)
            try:
                await self.music.join_group_call(
                    chat_id, input_stream, stream_type=StreamType().pulse_stream
                )
            except Exception as e:
                await self.leave_vc(chat_id)
                raise JoinVCException(f"[JoinVCException]: {e}")
        except AlreadyJoinedError:
            raise UserException(
                f"[UserException]: Already joined in the voice chat. If this is a mistake then try to restart the voice chat."
            )
        except Exception as e:
            raise UserException(f"[UserException]: {e}")

        await db.add_active_vc(chat_id, "video" if video else "voice")
        self.audience[chat_id] = {}
        users = await self.vc_participants(chat_id)
        user_ids = [user.user_id for user in users]
        await self.autoend(chat_id, user_ids)

    async def join_gc(self, chat_id: int):
        try:
            try:
                get = await hellbot.app.get_chat_member(chat_id, hellbot.user.id)
            except ChatAdminRequired:
                raise UserException(
                    f"[UserException]: Bot is not admin in chat {chat_id}"
                )
            if (
                get.status == ChatMemberStatus.RESTRICTED
                or get.status == ChatMemberStatus.BANNED
            ):
                raise UserException(
                    f"[UserException]: Assistant is restricted or banned in chat {chat_id}"
                )
        except UserNotParticipant:
            chat = await hellbot.app.get_chat(chat_id)
            if chat.username:
                try:
                    await hellbot.user.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise UserException(f"[UserException]: {e}")
            else:
                try:
                    try:
                        link = chat.invite_link
                        if link is None:
                            link = await hellbot.app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        raise UserException(
                            f"[UserException]: Bot is not admin in chat {chat_id}"
                        )
                    except Exception as e:
                        raise UserException(f"[UserException]: {e}")
                    hell = await hellbot.app.send_message(
                        chat_id, "Inviting assistant to chat..."
                    )
                    if link.startswith("https://t.me/+"):
                        link = link.replace("https://t.me/+", "https://t.me/joinchat/")
                    await hellbot.user.join_chat(link)
                    await hell.edit_text("Assistant joined the chat! Enjoy your music!")
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise UserException(f"[UserException]: {e}")


hellmusic = HellMusic()
