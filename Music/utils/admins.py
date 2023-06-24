from pyrogram.enums import ChatMembersFilter

from Music.core.clients import hellbot
from Music.core.database import db


async def get_admins(chat_id: int):
    admins = []
    async for x in hellbot.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        admins.append(x.user.id)
    return admins


async def get_auth_users(chat_id: int):
    auth_users = []
    async for x in hellbot.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        auth_users.append(x.user.id)
    users = await db.get_all_authusers(chat_id)
    if users:
        auth_list = list(users[chat_id].keys())
        auth_users.extend(auth_list)
    return auth_users