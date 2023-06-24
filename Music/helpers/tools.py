import asyncio
import os


async def runcmd(cmd: str):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stderr:
        if "unavailable videos are hidden" in (stderr.decode("utf-8")).lower():
            return stdout.decode("utf-8")
        else:
            return stderr.decode("utf-8")
    return stdout.decode("utf-8")


async def absolute_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


vid_formats = [
    "3g2",
    "3gp",
    "amv",
    "asf",
    "avi",
    "f4a",
    "f4b",
    "f4p",
    "f4v",
    "flv",
    "flv",
    "gifv",
    "m4p",
    "m4v",
    "m4v",
    "mkv",
    "mng",
    "mov",
    "mp2",
    "mp4",
    "mpe",
    "mpeg",
    "mpg",
    "mpv",
    "mxf",
    "nsv",
    "ogg",
    "ogv",
    "qt",
    "rm",
    "roq",
    "rrc",
    "svi",
    "vob",
    "webm",
    "wmv",
    "yuv",
]

themes = [
    "3024-night",
    "a11y-dark",
    "base16-dark",
    "base16-light",
    "blackboard",
    "cobalt",
    "dracula-pro",
    "duotone-dark",
    "hopscotch",
    "lucario",
    "material",
    "monokai",
    "nightowl",
    "nord",
    "oceanic-next",
    "one-dark",
    "one-light",
    "panda-syntax",
    "parasio-dark",
    "seti",
    "shades-of-purple",
    "solarized+dark",
    "solarized+light",
    "synthwave-84",
    "twilight",
    "verminal",
    "vscode",
    "yeti",
    "zenburn",
]

colour = [
    "#000000",
    "#0000FF",
    "#008000",
    "#008080",
    "#00FF00",
    "#00FFFF",
    "#00FFFF",
    "#30D5C8",
    "#4B0082",
    "#800000",
    "#800080",
    "#808000",
    "#808080",
    "#A52A2A",
    "#D2B48C",
    "#EE82EE",
    "#FF0000",
    "#FF00FF",
    "#FF5733",
    "#FFC0CB",
    "#FFFF00",
    "#FFFFFF",
]
