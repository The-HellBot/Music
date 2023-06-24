from pyrogram import filters
from pyrogram.types import Message

from config import Config
from Music.core import LOGS, db, hellbot


@hellbot.app.on_message(filters.private, group=1)
async def new_users(_, msg: Message):
    chat_id = msg.from_user.id
    if not await db.is_user_exist(chat_id):
        BOT_USERNAME = hellbot.app.username
        await db.add_user(chat_id)
        if Config.LOGGER_ID:
            await hellbot.logit(
                "newuser",
                f"**User:** {msg.from_user.mention(style='md')}\n**ID:** `{msg.from_user.id}`\n__Started @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(
                f"#NewUser: \n\nName: {msg.from_user.first_name} \nID: {msg.from_user.id}"
            )
    await msg.continue_propagation()


@hellbot.app.on_message(filters.group, group=2)
async def new_users(_, msg: Message):
    chat_id = msg.chat.id
    if not await db.is_chat_exist(chat_id):
        BOT_USERNAME = hellbot.app.username
        await db.add_chat(chat_id)
        if Config.LOGGER_ID:
            await hellbot.logit(
                "newchat",
                f"**Chat Title:** {msg.chat.title} \n**Chat UN:** @{msg.chat.username or None}) \n**Chat ID:** `{chat_id}` \n__ADDED @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(
                f"#NEWCHAT: \n\nChat Title: {msg.chat.title} \nChat UN: @{msg.chat.username}) \nChat ID: {chat_id} \n\nADDED @{BOT_USERNAME} !!",
            )
    await msg.continue_propagation()
