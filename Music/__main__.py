from pyrogram import idle

from config import Config
from Music.core.calls import hellmusic
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.core.users import user_data
from Music.helpers.strings import TEXTS
from Music.version import __version__


async def start_bot():
    hmusic_version = __version__["Hell Music"]
    py_version = __version__["Python"]
    pyro_version = __version__["Pyrogram"]
    pycalls_version = __version__["PyTgCalls"]

    LOGS.info("All Checks Completed! Let's Start Hell-Music...")

    await user_data.setup()
    await hellbot.start()
    await hellmusic.start()
    await hellmusic.decorators()
    await db.connect()

    try:
        if Config.BOT_PIC:
            await hellbot.app.send_photo(
                int(Config.LOGGER_ID),
                Config.BOT_PIC,
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    hmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    hellbot.app.mention(style="md"),
                ),
            )
        else:
            await hellbot.app.send_message(
                int(Config.LOGGER_ID),
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    hmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    hellbot.app.mention(style="md"),
                ),
            )
    except Exception as e:
        LOGS.warning(f"Error in Logger: {e}")

    LOGS.info(f"Hell-Music [{hmusic_version}] is now online!")

    await idle()

    await hellbot.app.send_message(
        Config.LOGGER_ID,
        f"#STOP \n\n**Hell-Music [{hmusic_version}] is now offline!**",
    )
    LOGS.info(f"Hell-Music [{hmusic_version}] is now offline!")


if __name__ == "__main__":
    hellbot.run(start_bot())
