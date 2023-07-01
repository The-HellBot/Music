import datetime
import random
import re
import string
import time

import aiohttp
import psutil
import pytz
from html_telegraph_poster import TelegraphPoster

from config import Config
from Music.version import __start_time__


class Formatters:
    def __init__(self) -> None:
        self.time_zone = pytz.timezone(Config.TZ)

    def check_limit(self, check: int, config: int) -> bool:
        if config == 0:
            return True
        if check == config:
            return True
        elif check < config:
            return True
        else:
            return False

    def mins_to_secs(self, time: str) -> int:
        out_time = sum(
            int(x) * 60**i for i, x in enumerate(reversed(time.split(":")))
        )
        return out_time

    def secs_to_mins(self, seconds: int) -> str:
        out_time = str(datetime.timedelta(seconds=seconds))
        if out_time.startswith("0:"):
            out_time = out_time[2:]
        return out_time

    def get_readable_time(self, seconds: int) -> str:
        count = 0
        ping_time = ""
        time_list = []
        time_suffix_list = ["s", "m", "h", "days"]
        while count < 4:
            count += 1
            if count < 3:
                remainder, result = divmod(seconds, 60)
            else:
                remainder, result = divmod(seconds, 24)
            if seconds == 0 and remainder == 0:
                break
            time_list.append(int(result))
            seconds = int(remainder)
        for i in range(len(time_list)):
            time_list[i] = str(time_list[i]) + time_suffix_list[i]
        if len(time_list) == 4:
            ping_time += time_list.pop() + ", "
        time_list.reverse()
        ping_time += ":".join(time_list)
        return ping_time

    def bytes_to_mb(self, size: int) -> int:
        mega_bytes = int(round(size / 1024 / 1024, 2))
        return mega_bytes

    def gen_key(self, message: str, volume: int = 5) -> str:
        key = f"{message}_" + "".join(
            [random.choice(string.ascii_letters) for i in range(volume)]
        )
        return key

    def group_the_list(self, collection: list, group: int = 5, length: bool = False):
        kbs = [collection[i : i + group] for i in range(0, len(collection), group)]
        total = 0
        for i in kbs:
            total += len(i)
        if length:
            kbs = len(kbs)
        return kbs, total

    async def system_stats(self) -> dict:
        bot_uptime = int(time.time() - __start_time__)
        cpu = psutil.cpu_percent(interval=0.5)
        core = psutil.cpu_count()
        disk = psutil.disk_usage("/").percent
        ram = psutil.virtual_memory().percent
        uptime = f"{self.get_readable_time((bot_uptime))}"
        context = {
            "cpu": f"{cpu}%",
            "core": core,
            "disk": f"{disk}%",
            "ram": f"{ram}%",
            "uptime": uptime,
        }
        return context

    def convert_telegraph_url(self, url: str) -> str:
        try:
            pattern = r"(https?://)(telegra\.ph)"
            converted_url = re.sub(pattern, r"\1te.legra.ph", url)
            return converted_url
        except:
            return url

    async def telegraph_paste(
        self,
        title: str,
        text: str,
        auth: str = "[ †he Hêllẞø† ]",
        url: str = "https://t.me/its_hellbot",
    ):
        client = TelegraphPoster(use_api=True)
        client.create_api_token(auth)
        post_page = client.post(
            title=title,
            author=auth,
            author_url=url,
            text=text,
        )
        return self.convert_telegraph_url(post_page["url"])

    async def post(self, url: str, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, *args, **kwargs) as resp:
                try:
                    data = await resp.json()
                except Exception:
                    data = await resp.text()
            return data

    async def bb_paste(self, text):
        BASE = "https://batbin.me/"
        resp = await self.post(f"{BASE}api/v2/paste", data=text)
        if not resp["success"]:
            return
        link = BASE + resp["message"]
        return link


formatter = Formatters()
