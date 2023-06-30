import datetime

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from config import Config
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.decorators import AdminWrapper, check_mode
from Music.helpers.formatters import formatter
from Music.utils.pages import MakePages


@hellbot.app.on_message(filters.command("auth") & filters.group & ~Config.BANNED_USERS)
@check_mode
@AdminWrapper
async def auth(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "Reply to a user or give a user id or username"
            )
        all_auths = await db.get_all_authusers(message.chat.id)
        count = len(all_auths)
        if count == 30:
            return await message.reply_text(
                "AuthList is full! \n\nLimit of Auth Users in a chat is: `30`"
            )
        user = message.text.split(" ", 1)[1]
        user = user.replace("@", "")
        user = await hellbot.app.get_users(user)
        is_auth = await db.is_authuser(message.chat.id, user.id)
        if not is_auth:
            context = {
                "user_name": user.first_name,
                "auth_by_id": message.from_user.id,
                "auth_by_name": message.from_user.first_name,
                "auth_date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            }
            await db.add_authusers(message.chat.id, user.id, context)
            await message.reply_text("Successfully Authorized user in this chat!")
        else:
            await message.reply_text("This user is already Authorized in this chat!")
    else:
        all_auths = await db.get_all_authusers(message.chat.id)
        count = len(all_auths)
        if count == 30:
            return await message.reply_text(
                "AuthList is full! \n\nLimit of Auth Users in a chat is: `30`"
            )
        user = message.reply_to_message.from_user
        is_auth = await db.is_authuser(message.chat.id, user.id)
        if not is_auth:
            context = {
                "user_name": user.first_name,
                "auth_by_id": message.from_user.id,
                "auth_by_name": message.from_user.first_name,
                "auth_date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            }
            await db.add_authusers(message.chat.id, user.id, context)
            await message.reply_text("Successfully Authorized user in this chat!")
        else:
            await message.reply_text("This user is already Authorized in this chat!")


@hellbot.app.on_message(
    filters.command("unauth") & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AdminWrapper
async def unauth(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "Reply to a user or give a user id or username"
            )
        user = message.text.split(None, 1)[1]
        user = user.replace("@", "")
        user = await hellbot.app.get_users(user)
        is_auth = await db.is_authuser(message.chat.id, user.id)
        if is_auth:
            await db.remove_authuser(message.chat.id, user.id)
            await message.reply_text("Removed user's Authorization in this chat!")
        else:
            await message.reply_text("This user was not Authorized in this chat!")
    else:
        user = message.reply_to_message.from_user
        is_auth = await db.is_authuser(message.chat.id, user.id)
        if is_auth:
            await db.remove_authuser(message.chat.id, user.id)
            await message.reply_text("Removed user's Authorization in this chat!")
        else:
            await message.reply_text("This user was not Authorized in this chat!")


@hellbot.app.on_message(
    filters.command("authlist") & filters.group & ~Config.BANNED_USERS
)
@check_mode
async def authusers(_, message: Message):
    all_auths = await db.get_all_authusers(message.chat.id)
    if not all_auths:
        await message.reply_text("No Authorized users in this chat!")
    else:
        hell = await message.reply_text("Fetching Authorized users in this chat ...")
        collection = []
        for user in all_auths:
            data = await db.get_authuser(message.chat.id, user)
            user_name = data["user_name"]
            admin_id = data["auth_by_id"]
            admin_name = data["auth_by_name"]
            auth_date = data["auth_date"]
            context = {
                "auth_user": user_name,
                "admin_id": admin_id,
                "admin_name": admin_name,
                "auth_date": auth_date,
            }
            collection.append(context)
        rand_key = formatter.gen_key(f"auth{message.chat.id}", 4)
        Config.CACHE[rand_key] = collection
        await MakePages.authusers_page(hell, rand_key, 0, 0, True)


@hellbot.app.on_message(
    filters.command("authchat") & filters.group & ~Config.BANNED_USERS
)
@AdminWrapper
async def settings(_, message: Message):
    is_auth = await db.is_authchat(message.chat.id)
    if len(message.command) != 2:
        return await message.reply_text(
            f"Current AuthChat Status: `{'On' if is_auth else 'Off'}`\n\nUsage: `/authchat on` or `/authchat off`"
        )
    if message.command[1] == "on":
        if is_auth:
            await message.reply_text("AuthChat is already On!")
        else:
            await db.add_authchat(message.chat.id)
            await message.reply_text(
                "**Turned On AuthChat!** \n\nNow all users can use bot commands in this chat!"
            )
    elif message.command[1] == "off":
        if is_auth:
            await db.remove_authchat(message.chat.id)
            await message.reply_text(
                "**Turned Off AuthChat!** \n\nNow only Authorized users can use bot commands in this chat!"
            )
        else:
            await message.reply_text("AuthChat is already Off!")
    else:
        await message.reply_text(
            f"Current AuthChat Status: `{'On' if is_auth else 'Off'}`\n\nUsage: `/authchat on` or `/authchat off`"
        )


@hellbot.app.on_callback_query(filters.regex(r"authus") & ~Config.BANNED_USERS)
async def activevc_cb(_, cb: CallbackQuery):
    _, action, page, rand_key = cb.data.split("_")
    if action == "close":
        Config.CACHE.pop(rand_key)
        await cb.message.delete()
    else:
        collection = Config.CACHE[rand_key]
        length = len(collection) - 1
        if int(page) == 0 and action == "prev":
            page = length
        elif int(page) == length and action == "next":
            page = 0
        else:
            page = int(page) + 1 if action == "next" else int(page) - 1
        index = page * 6
        await MakePages.authusers_page(cb, rand_key, page, index, True)
