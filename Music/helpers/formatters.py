import random
import string


def gen_key(message: str, volume: int = 5) -> str:
    key = f"{message}_" + "".join(
        [random.choice(string.ascii_letters) for i in range(volume)]
    )
    return key