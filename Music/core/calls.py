from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.raw.types import InputPeerChannel
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import GroupCallNotFound, NoActiveGroupCall
from pytgcalls.types import JoinedGroupCallParticipant, LeftGroupCallParticipant, Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import MediumQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

from config import Config
from Music.helpers.buttons import MakeButtons
from Music.helpers.strings import TEXTS
from Music.utils.auto_cmds import autoclean, autoend
from Music.utils.exceptions import UserException
from Music.utils.queue import Queue
from Music.utils.thumbnail import thumbnail
from Music.utils.youtube import ytube

from .clients import hellbot
from .database import db
from .logger import LOGS


class HellMusic(PyTgCalls):
    def __ini__(self):
        self.music = PyTgCalls(hellbot.user)
        self.audience = {}

    async def __clean__(self, chat_id: int):
        Queue.clear_queue(chat_id)
        await db.remove_active_vc(chat_id)

    async def start(self):
        LOGS.info(">> Booting PyTgCalls Client...")
        if Config.HELLBOT_SESSION:
            await self.music.start()
            LOGS.info(">> Booted PyTgCalls Client!")
        else:
            LOGS.error(">> PyTgCalls Client not booted!")
            quit(1)

    async def ping(self):
        pinged = await self.music.ping()
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

    async def leave_vc(self, chat_id: int):
        await self.__clean__(chat_id)
        await self.music.leave_group_call(chat_id)

    async def skip_vc(self, chat_id: int, file_path: str, video: bool = False):
        if video:
            input_stream = AudioVideoPiped(
                file_path, MediumQualityAudio(), MediumQualityVideo()
            )
        else:
            input_stream = AudioPiped(file_path, MediumQualityAudio())
        await self.music.change_stream(chat_id, input_stream)

    async def invited_vc(self, chat_id: int):
        try:
            await hellbot.app.send_message(
                chat_id, "The Bot will join vc only when you give something to play!"
            )
        except:
            return

    async def change_vc(self, chat_id: int):
        get = Queue.get_queue(chat_id)
        try:
            if not get:
                return await self.leave_vc(chat_id)

            loop = await db.get_loop(chat_id)
            if loop == 0:
                clean = get.pop(0)
                await autoclean(clean)
            else:
                await db.set_loop(chat_id, loop - 1)
        except:
            return await self.leave_vc(chat_id)
        # get = Queue.get_queue(chat_id)
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
                success, to_stream = await ytube.download(video_id, True)
                if not success:
                    raise UserException(f"[UserException - change_vc]: {to_stream}")
            if vc_type == "video":
                input_stream = AudioVideoPiped(
                    queue, MediumQualityAudio(), MediumQualityVideo()
                )
            else:
                input_stream = AudioPiped(queue, MediumQualityAudio())
            try:
                photo = thumbnail.generate((359), (297, 302), video_id)
                await self.music.change_stream(int(chat_id), input_stream)
                btns = MakeButtons.player_markup(
                    chat_id, "None" if video_id == "telegram" else video_id
                )
                if photo:
                    await hellbot.app.send_photo(
                        int(chat_id),
                        photo,
                        TEXTS.PLAYING.format(
                            Config.BOT_NAME,
                            title,
                            duration,
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(btns),
                    )
                else:
                    await hellbot.app.send_message(
                        int(chat_id),
                        TEXTS.PLAYING.format(
                            Config.BOT_NAME,
                            title,
                            duration,
                            user,
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(btns),
                    )
            except Exception as e:
                raise UserException(f"[UserException - change_vc]: {e}")

    async def join_vc(self, chat_id: int, file_path: str, video: bool = False):
        audio_quality = MediumQualityAudio()
        video_quality = MediumQualityVideo()
        if video:
            input_stream = AudioVideoPiped(file_path, audio_quality, video_quality)
        else:
            input_stream = AudioPiped(file_path, audio_quality)
        try:
            await self.music.join_group_call(
                chat_id, input_stream, stream_type=StreamType().pulse_stream
            )
        except (NoActiveGroupCall, GroupCallNotFound):
            try:
                peer = await hellbot.user.resolve_peer(chat_id)
                await hellbot.user.send(
                    CreateGroupCall(
                        peer=InputPeerChannel(
                            channel_id=peer.channel_id,
                            access_hash=peer.access_hash,
                        ),
                        random_id=hellbot.user.rnd_id() // 9000000000,
                    )
                )
                return await self.join_vc(chat_id, file_path, video)
            except:
                raise UserException(
                    f"[UserException - join_vc]: Assistant is having trouble starting the voice chat! Please start it manually!"
                )
        except Exception as e:
            raise UserException(f"[UserException - join_vc]: {e}")
        await db.add_active_vc(chat_id, "video" if video else "voice")
        self.audience[chat_id] = {}
        await autoend(chat_id)

    async def join_gc(self, chat_id: int):
        try:
            try:
                get = await hellbot.app.get_chat_member(chat_id, hellbot.user.id)
            except ChatAdminRequired:
                raise UserException(
                    f"[UserException - join_gc]: Bot is not admin in chat {chat_id}"
                )
            if get.status == ChatMemberStatus.RESTRICTED or ChatMemberStatus.BANNED:
                raise UserException(
                    f"[UserException - join_gc]: Bot is restricted or banned in chat {chat_id}"
                )
        except UserNotParticipant:
            chat = await hellbot.app.get_chat(chat_id)
            if chat.username:
                try:
                    await hellbot.user.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise UserException(f"[UserException - join_gc]: {e}")
            else:
                try:
                    try:
                        link = chat.invite_link
                        if link is None:
                            link = await hellbot.app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        raise UserException(
                            f"[UserException - join_gc]: Bot is not admin in chat {chat_id}"
                        )
                    except Exception as e:
                        raise UserException(f"[UserException - join_gc]: {e}")
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
                    raise UserException(f"[UserException - join_gc]: {e}")

    async def decorators(self):
        @self.music.on_closed_voice_chat()
        @self.music.on_kicked()
        @self.music.on_left()
        async def stream_end(chat_id: int):
            await self.leave_vc(chat_id)

        @self.music.on_group_call_invite()
        async def invite_to_call(chat_id: int):
            await self.invited_vc(chat_id)

        @self.music.on_participants_change()
        async def members_changed(update: Update):
            if not isinstance(update, JoinedGroupCallParticipant) and not isinstance(
                update, LeftGroupCallParticipant
            ):
                return
            try:
                chat_id = update.chat_id
                audience = self.audience.get(chat_id)
                if not audience:
                    await autoend(chat_id)
                else:
                    new = (
                        audience + 1
                        if isinstance(update, JoinedGroupCallParticipant)
                        else audience - 1
                    )
                    self.audience[chat_id] = new
                    await autoend(chat_id)
            except:
                return

        @self.music.on_stream_end()
        async def update_stream(update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_vc(update.chat_id)


hellmusic = HellMusic()
