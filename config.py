from os import environ

from pyrogram import filters


class Config(object):
    # required config variables
    API_HASH = environ.get("API_HASH", None)                # get from my.telegram.org
    API_ID = int(environ.get("API_ID", 0))                  # get from my.telegram.org
    BOT_TOKEN = environ.get("BOT_TOKEN", None)              # get from @BotFather
    DATABASE_URL = environ.get("DATABASE_URL", None)        # from https://cloud.mongodb.com/
    HELLBOT_SESSION = environ.get("HELLBOT_SESSION", None)  # enter your session string here
    LOGGER_ID = int(environ.get("LOGGER_ID", 0))            # make a channel and get its ID
    OWNER_ID = environ.get("OWNER_ID", "")                  # enter your id here

    # heroku variables only
    HEROKU_API = environ.get("HEROKU_API", None)    # from https://dashboard.heroku.com/account
    HEROKU_APP = environ.get("HEROKU_APP", None)    # enter your app name here

    # optional config variables
    BLACK_IMG = environ.get("BLACK_IMG", "https://telegra.ph/file/2c546060b20dfd7c1ff2d.jpg")       # black image for progress
    BOT_NAME = environ.get("BOT_NAME", "\x40\x4d\x75\x73\x69\x63\x5f\x48\x65\x6c\x6c\x42\x6f\x74")  # dont put fancy texts here.
    BOT_PIC = environ.get("BOT_PIC", "https://te.legra.ph/file/5d5642103804ae180e40b.jpg")          # put direct link to image here
    LYRICS_API = environ.get("LYRICS_API", None)            # from https://docs.genius.com/
    MAX_FAVORITES = int(environ.get("MAX_FAVORITES", 30))  # max number of favorite tracks
    PLAY_LIMIT = int(environ.get("PLAY_LIMIT", 0))          # time in minutes. 0 for no limit
    PRIVATE_MODE = environ.get("PRIVATE_MODE", "off")       # "on" or "off" to enable/disable private mode
    SONG_LIMIT = int(environ.get("SONG_LIMIT", 0))          # time in minutes. 0 for no limit
    TELEGRAM_IMG = environ.get("TELEGRAM_IMG", None)        # put direct link to image here
    TG_AUDIO_SIZE_LIMIT = int(environ.get("TG_AUDIO_SIZE_LIMIT", 104857600))    # size in bytes. 0 for no limit
    TG_VIDEO_SIZE_LIMIT = int(environ.get("TG_VIDEO_SIZE_LIMIT", 1073741824))   # size in bytes. 0 for no limit
    TZ = environ.get("TZ", "Asia/Kolkata")  # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

    # do not edit these variables
    BANNED_USERS = filters.user()
    CACHE = {}
    CACHE_DIR = "./cache/"
    DELETE_DICT = {}
    DWL_DIR = "./downloads/"
    GOD_USERS = filters.user()
    PLAYER_CACHE = {}
    QUEUE_CACHE =  {}
    SONG_CACHE = {}
    SUDO_USERS = filters.user()


# get all config variables in a list
all_vars = [i for i in Config.__dict__.keys() if not i.startswith("__")]