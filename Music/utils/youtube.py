import os
import re
import time

import requests
import yt_dlp
from lyricsgenius import Genius
from pyrogram.types import CallbackQuery
from youtubesearchpython.__future__ import VideosSearch

from config import Config
from Music.core.clients import hellbot
from Music.core.logger import LOGS
from Music.helpers.strings import TEXTS


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="
        self.regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/|youtube\.com\/playlist\?list=)"
        self.audio_opts = {"format": "bestaudio[ext=m4a]"}
        self.video_opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        self.yt_opts_audio = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        }
        self.yt_opts_video = {
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        }
        self.yt_playlist_opts = {
            "exctract_flat": True,
        }
        self.lyrics = Config.LYRICS_API
        try:
            if self.lyrics:
                self.client = Genius(self.lyrics, remove_section_headers=True)
            else:
                self.client = None
        except Exception as e:
            LOGS.warning(f"[Exception in Lyrics API]: {e}")
            self.client = None

    def check(self, link: str):
        return bool(re.match(self.regex, link))

    async def format_link(self, link: str, video_id: bool) -> str:
        link = link.strip()
        if video_id:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        return link

    async def get_data(self, link: str, video_id: bool, limit: int = 1) -> list:
        yt_url = await self.format_link(link, video_id)
        collection = []
        results = VideosSearch(yt_url, limit=limit)
        for result in (await results.next())["result"]:
            vid = result["id"]
            channel = result["channel"]["name"]
            channel_url = result["channel"]["link"]
            duration = result["duration"]
            published = result["publishedTime"]
            thumbnail = f"https://i.ytimg.com/vi/{result['id']}/hqdefault.jpg"
            title = result["title"]
            url = result["link"]
            views = result["viewCount"]["short"]
            context = {
                "id": vid,
                "ch_link": channel_url,
                "channel": channel,
                "duration": duration,
                "link": url,
                "published": published,
                "thumbnail": thumbnail,
                "title": title,
                "views": views,
            }
            collection.append(context)
        return collection[:limit]

    async def get_playlist(self, link: str) -> list:
        yt_url = await self.format_link(link, False)
        with yt_dlp.YoutubeDL(self.yt_playlist_opts) as ydl:
            results = ydl.extract_info(yt_url, False)
            playlist = [video['id'] for video in results['entries']]
        return playlist

    async def download(self, link: str, video_id: bool, video: bool = False) -> str:
        yt_url = await self.format_link(link, video_id)
        if video:
            dlp = yt_dlp.YoutubeDL(self.yt_opts_video)
            info = dlp.extract_info(yt_url, False)
        else:
            dlp = yt_dlp.YoutubeDL(self.yt_opts_audio)
            info = dlp.extract_info(yt_url, False)
        path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if not os.path.exists(path):
            dlp.download([yt_url])
        return path

    async def send_song(
        self, message: CallbackQuery, rand_key: str, key: int, video: bool = False
    ) -> dict:
        track = Config.SONG_CACHE[rand_key][key]
        ydl_opts = self.video_opts if video else self.audio_opts
        hell = await message.message.reply_text("Downloading...")
        await message.message.delete()
        try:
            output = None
            thumb = f"{track['id']}{time.time()}.jpg"
            _thumb = requests.get(track["thumbnail"], allow_redirects=True)
            open(thumb, "wb").write(_thumb.content)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                yt_file = ydl.extract_info(track["link"], download=video)
                if not video:
                    output = ydl.prepare_filename(yt_file)
                    ydl.process_info(yt_file)
                    await message.message.reply_audio(
                        audio=output,
                        caption=TEXTS.SONG_CAPTION.format(
                            track["title"],
                            track["link"],
                            track["views"],
                            track["duration"],
                            message.from_user.mention,
                            hellbot.app.mention,
                        ),
                        duration=int(yt_file["duration"]),
                        performer=TEXTS.PERFORMER,
                        title=yt_file["title"],
                        thumb=thumb,
                    )
                else:
                    output = f"{yt_file['id']}.mp4"
                    await message.message.reply_video(
                        video=output,
                        caption=TEXTS.SONG_CAPTION.format(
                            track["title"],
                            track["link"],
                            track["views"],
                            track["duration"],
                            message.from_user.mention,
                            hellbot.app.mention,
                        ),
                        duration=int(yt_file["duration"]),
                        thumb=thumb,
                        supports_streaming=True,
                    )
            chat = message.message.chat.title or message.message.chat.first_name
            await hellbot.logit(
                "Video" if video else "Audio",
                f"**⤷ User:** {message.from_user.mention} [`{message.from_user.id}`]\n**⤷ Chat:** {chat} [`{message.message.chat.id}`]\n**⤷ Link:** [{track['title']}]({track['link']})",
            )
            await hell.delete()
        except Exception as e:
            await hell.edit_text(f"**Error:**\n`{e}`")
        try:
            Config.SONG_CACHE.pop(rand_key)
            os.remove(thumb)
            os.remove(output)
        except Exception:
            pass

    async def get_lyrics(self, song: str, artist: str) -> dict:
        context = {}
        if not self.client:
            return context
        results = self.client.search_song(song, artist)
        if results:
            results.to_dict()
            title = results["full_title"]
            image = results["song_art_image_url"]
            lyrics = results["lyrics"]
            context = {
                "title": title,
                "image": image,
                "lyrics": lyrics,
            }
        return context


ytube = YouTube()
