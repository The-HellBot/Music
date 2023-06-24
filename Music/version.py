import platform

from pyrogram import __version__ as pyro_version
from pytgcalls.__version__ import __version__ as pytgcalls_version

# versions dictionary
__version__ = {
    "Hell Music": "0.0.1",
    "Python": platform.python_version(),
    "Pyrogram": pyro_version,
    "PyTgCalls": pytgcalls_version,
}