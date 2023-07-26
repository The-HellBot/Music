from pyrogram.enums import ChatMembersFilter, ChatMemberStatus

from Music.core.clients import hellbot
from Music.core.database import db


async def get_admins(chat_id: int):
    admins = []
    async for x in hellbot.app.get_chat_members(
        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        admins.append(x.user.id)
    return admins


async def get_auth_users(chat_id: int):
    auth_users = []
    async for x in hellbot.app.get_chat_members(
        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        auth_users.append(x.user.id)
    users = await db.get_all_authusers(chat_id)
    if users:
        auth_users.extend(users)
    return auth_users


async def get_user_rights(chat_id: int, user_id: int):
    try:
        user = await hellbot.app.get_chat_member(chat_id, user_id)
    except:
        return False
    if user.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    if user.privileges.can_manage_video_chats:
        return True
    return False


async def get_user_type(chat_id: int, user_id: int):
    admins = await get_admins(chat_id)
    auth_users = await get_auth_users(chat_id)
    if user_id in admins:
        return "admin"
    if user_id in auth_users:
        return "auth"
    return "user"
