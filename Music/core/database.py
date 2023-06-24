import datetime
import sys

from motor.motor_asyncio import AsyncIOMotorClient

from config import Config

from .logger import LOGS


class Database(object):
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.DATABASE_URL)
        self.db = self.client["HellMusicDB"]

        # mongo db collections
        self.authusers = self.db.authusers
        self.authchats = self.db.authchats
        self.bl_chats = self.db.bl_chats
        self.blocked_users = self.db.blocked_users
        self.chats = self.db.chats
        self.gban_db = self.db.gban_db
        self.gcast = self.db.gcast
        self.sudousers = self.db.sudousers
        self.users = self.db.users

        # local db collections
        self.active_vc = [{"chat_id": 0, "join_time": 0, "vc_type": "voice"}]
        self.autoend = {}
        self.loop = {}

    # database connection #
    async def connect(self):
        try:
            self.client.admin.command("ping")
            LOGS.info(">> Database connection successful!")
        except Exception as e:
            LOGS.error(f"Database connection failed: '{e}'")
            sys.exit()

    # users db #
    async def add_user(self, user_id: int):
        context = {
            "user_id": user_id,
            "join_date": datetime.datetime.now(),
            "songs_played": 0,
            "level": 0,
        }
        await self.users.insert_one(context)

    async def delete_user(self, user_id: int):
        await self.users.delete_one({"user_id": user_id})

    async def is_user_exist(self, user_id: int) -> bool:
        user = await self.users.find_one({"user_id": user_id})
        return bool(user)

    async def get_user(self, user_id: int):
        user = await self.users.find_one({"user_id": user_id})
        return user

    async def get_all_users(self):
        users = self.users.find({})
        return users

    async def total_users_count(self):
        count = await self.users.count_documents({})
        return count

    # chat db #
    async def add_chat(self, chat_id: int):
        context = {
            "chat_id": chat_id,
            "join_date": datetime.datetime.now(),
            "autoend": True,
        }
        await self.chats.insert_one(context)

    async def delete_chat(self, chat_id: int):
        await self.chats.delete_one({"chat_id": chat_id})

    async def is_chat_exist(self, chat_id: int) -> bool:
        chat = await self.chats.find_one({"chat_id": chat_id})
        return bool(chat)

    async def get_chat(self, chat_id: int):
        chat = await self.chats.find_one({"chat_id": chat_id})
        return chat

    async def get_all_chats(self):
        chats = self.chats.find({})
        return chats

    async def total_chats_count(self):
        count = await self.chats.count_documents({})
        return count

    # active vc db #
    async def get_active_vc(self) -> list:
        return self.active_vc

    async def add_active_vc(self, chat_id: int, vc_type: str):
        cid = [x["chat_id"] for x in self.active_vc]
        if not chat_id in cid:
            self.active_vc.append(
                {
                    "chat_id": chat_id,
                    "join_time": datetime.datetime.now(),
                    "vc_type": vc_type,
                }
            )

    async def is_active_vc(self, chat_id: int) -> bool:
        cid = [x["chat_id"] for x in self.active_vc]
        if chat_id not in cid:
            return False
        else:
            return True

    async def remove_active_vc(self, chat_id: int):
        for x in self.active_vc:
            if x["chat_id"] == chat_id:
                self.active_vc.remove(x)

    # autoend db #
    async def get_autoend(self, chat_id: int):
        chat = await self.chats.find_one({"chat_id": chat_id})
        if chat:
            return chat["autoend"]
        else:
            return False

    async def set_autoend(self, chat_id: int, autoend: bool):
        chat = await self.chats.find_one({"chat_id": chat_id})
        if chat:
            await self.chats.update_one(
                {"chat_id": chat_id}, {"$set": {"autoend": autoend}}
            )
        else:
            await self.add_chat(chat_id)
            await self.chats.update_one(
                {"chat_id": chat_id}, {"$set": {"autoend": autoend}}
            )

    # loop db #
    async def set_loop(self, chat_id: int, loop: int):
        self.loop[chat_id] = loop

    async def get_loop(self, chat_id: int) -> int:
        loop = self.loop.get(chat_id)
        return loop or 0

    # sudousers db #
    async def get_sudo_users(self) -> list:
        users = await self.sudousers.find_one({"sudo": "sudo"})
        if not users:
            return []
        return users["user_ids"]

    async def add_sudo(self, user_id: int) -> bool:
        users = await self.get_sudo_users()
        users.append(user_id)
        await self.sudousers.update_one(
            {"sudo": "sudo"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    async def remove_sudo(self, user_id: int) -> bool:
        users = await self.get_sudo_users()
        users.remove(user_id)
        await self.sudousers.update_one(
            {"sudo": "sudo"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    # blocked users db #
    async def get_blocked_users(self) -> list:
        users = await self.blocked_users.find_one({"blocked": "blocked"})
        if not users:
            return []
        return users["user_ids"]

    async def add_blocked_user(self, user_id: int) -> bool:
        users = await self.get_blocked_users()
        users.append(user_id)
        await self.blocked_users.update_one(
            {"blocked": "blocked"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    async def remove_blocked_user(self, user_id: int) -> bool:
        users = await self.get_blocked_users()
        users.remove(user_id)
        await self.blocked_users.update_one(
            {"blocked": "blocked"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    # gbanned users db #
    async def get_gbanned_users(self) -> list:
        users = await self.gban_db.find_one({"gbanned": "gbanned"})
        if not users:
            return []
        return users["user_ids"]

    async def add_gbanned_user(self, user_id: int) -> bool:
        users = await self.get_gbanned_users()
        users.append(user_id)
        await self.gban_db.update_one(
            {"gbanned": "gbanned"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    async def remove_gbanned_users(self, user_id: int) -> bool:
        users = await self.get_gbanned_users()
        users.remove(user_id)
        await self.gban_db.update_one(
            {"gbanned": "gbanned"}, {"$set": {"user_ids": users}}, upsert=True
        )
        return True

    # authusers db #
    async def add_authusers(self, chat_id: int, user_id: int, details: dict):
        context = {user_id: details}
        await self.authusers.insert_one({chat_id: context})

    async def is_authuser(self, chat_id: int, user_id: int) -> bool:
        chat = await self.authusers.find_one({chat_id: {user_id: {}}})
        return bool(chat)

    async def get_authuser(self, chat_id: int, user_id: int):
        chat = await self.authusers.find_one({chat_id: {user_id: {}}})
        return chat if chat else {}

    async def get_all_authusers(self, chat_id: int):
        all_users = await self.authusers.find_one({chat_id: {}})
        return all_users if all_users else {}

    async def remove_authuser(self, chat_id: int, user_id: int):
        await self.authusers.delete_one({chat_id: {user_id: {}}})

    # authchats db #
    async def get_authchats(self) -> list:
        chats = await self.authchats.find_one({"authchats": "authchats"})
        if not chats:
            return []
        return chats["chat_ids"]

    async def add_authchat(self, chat_id: int) -> bool:
        chats = await self.get_authchats()
        chats.append(chat_id)
        await self.authchats.update_one(
            {"authchats": "authchats"}, {"$set": {"chat_ids": chats}}, upsert=True
        )
        return True

    async def remove_authchat(self, chat_id: int) -> bool:
        chats = await self.get_authchats()
        chats.remove(chat_id)
        await self.authchats.update_one(
            {"authchats": "authchats"}, {"$set": {"chat_ids": chats}}, upsert=True
        )
        return True


db = Database()
