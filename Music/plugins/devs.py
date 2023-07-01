import io
import os
import re
import subprocess
import sys
import traceback

from pyrogram import filters
from pyrogram.types import Message

from config import Config, all_vars
from Music.core.clients import hellbot
from Music.core.database import db


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@hellbot.app.on_message(filters.command(["eval", "run"]) & Config.GOD_USERS)
async def eval(_, message: Message):
    hell = await message.reply_text("Processing ...")
    lists = message.text.split(" ", 1)
    if len(lists) != 2:
        return await hell.edit_text("Received empty message!")
    cmd = lists[1].strip()
    reply_to = message.reply_to_message or message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, hellbot, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to.reply_document(
                document=out_file, caption=cmd[:1000], disable_notification=True
            )
    else:
        await reply_to.reply_text(final_output)
    await hell.delete()


@hellbot.app.on_message(
    filters.command(["exec", "term", "sh", "shh"]) & Config.GOD_USERS
)
async def term(_, message: Message):
    hell = await message.reply_text("Processing ...")
    lists = message.text.split(" ", 1)
    if len(lists) != 2:
        return await hell.edit_text("Received empty message!")
    cmd = lists[1].strip()
    if "\n" in cmd:
        code = cmd.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await hell.edit(f"**Error:** \n`{err}`")
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(exc_type, exc_obj, exc_tb)
            await hell.edit("**Error:**\n`{}`".format("".join(errors)))
            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            filename = "output.txt"
            with open(filename, "w+") as file:
                file.write(output)
            await message.reply_document(
                filename,
                caption=f"`{cmd}`",
            )
            os.remove(filename)
            return
        await hell.edit(f"**Output:**\n`{output}`")
    else:
        await hell.edit("**Output:**\n`No Output`")


@hellbot.app.on_message(filters.command(["getvar", "gvar", "var"]) & Config.GOD_USERS)
async def varget_(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Give a variable name to get it's value.")
    check_var = message.text.split(None, 2)[1]
    if check_var.upper() not in all_vars:
        return await message.reply_text("Give a valid variable name to get it's value.")
    output = Config.__dict__[check_var.upper()]
    if not output:
        await message.reply_text("No Output Found!")
    else:
        return await message.reply_text(f"**{check_var}:** `{str(output)}`")


@hellbot.app.on_message(filters.command("addsudo") & Config.GOD_USERS)
async def useradd(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "Reply to a user or give a user id to add them as sudo."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await hellbot.app.get_users(user)
        if user.id in Config.SUDO_USERS:
            return await message.reply_text(f"{user.mention} is already a sudo user.")
        added = await db.add_sudo(user.id)
        if added:
            Config.SUDO_USERS.add(user.id)
            await message.reply_text(f"{user.mention} is now a sudo user.")
        else:
            await message.reply_text("Failed to add sudo user.")
        return
    if message.reply_to_message.from_user.id in Config.SUDO_USERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} is already a sudo user."
        )
    added = await db.add_sudo(message.reply_to_message.from_user.id)
    if added:
        Config.SUDO_USERS.add(message.reply_to_message.from_user.id)
        await message.reply_text(
            f"{message.reply_to_message.from_user.mention} is now a sudo user."
        )
    else:
        await message.reply_text("Failed to add sudo user.")
    return


@hellbot.app.on_message(filters.command(["delsudo", "rmsudo"]) & Config.GOD_USERS)
async def userdel(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "Reply to a user or give a user id to remove them from sudo."
            )
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await hellbot.app.get_users(user)
        if user.id not in Config.SUDO_USERS:
            return await message.reply_text(f"{user.mention} is not a sudo user.")
        removed = await db.remove_sudo(user.id)
        if removed:
            Config.SUDO_USERS.remove(user.id)
            await message.reply_text(f"{user.mention} is no longer a sudo user.")
            return
        await message.reply_text("Failed to remove sudo user.")
        return
    user_id = message.reply_to_message.from_user.id
    if user_id not in Config.SUDO_USERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} is not a sudo user."
        )
    removed = await db.remove_sudo(user_id)
    if removed:
        Config.SUDO_USERS.remove(user_id)
        await message.reply_text(
            f"{message.reply_to_message.from_user.mention} is no longer a sudo user."
        )
        return
    await message.reply_text("Failed to remove sudo user.")
