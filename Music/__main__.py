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

    LOGS.info(
        "\x41\x6c\x6c\x20\x43\x68\x65\x63\x6b\x73\x20\x43\x6f\x6d\x70\x6c\x65\x74\x65\x64\x21\x20\x4c\x65\x74\x27\x73\x20\x53\x74\x61\x72\x74\x20\x48\x65\x6c\x6c\x2d\x4d\x75\x73\x69\x63\x2e\x2e\x2e"
    )

    await user_data.setup()
    await hellbot.start()
    await hellmusic.start()
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
        LOGS.warning(
            f"\x45\x72\x72\x6f\x72\x20\x69\x6e\x20\x4c\x6f\x67\x67\x65\x72\x3a\x20{e}"
        )

    LOGS.info(
        f"\x3e\x3e\x20\x48\x65\x6c\x6c\x2d\x4d\x75\x73\x69\x63\x20\x5b{hmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x6e\x6c\x69\x6e\x65\x21"
    )

    await idle()

    await hellbot.app.send_message(
        Config.LOGGER_ID,
        f"\x23\x53\x54\x4f\x50\n\n**\x48\x65\x6c\x6c\x2d\x4d\x75\x73\x69\x63\x20\x5b{hmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x66\x66\x6c\x69\x6e\x65\x21**",
    )
    LOGS.info(
        f"\x48\x65\x6c\x6c\x2d\x4d\x75\x73\x69\x63\x20\x5b{hmusic_version}\x5d\x20\x69\x73\x20\x6e\x6f\x77\x20\x6f\x66\x66\x6c\x69\x6e\x65\x21"
    )


if __name__ == "__main__":
    hellbot.run(start_bot())
