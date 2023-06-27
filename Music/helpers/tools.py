async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


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
