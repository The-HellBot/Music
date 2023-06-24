from pyrogram.enums import MessageEntityType
from pyrogram.types import Message


class Player:
    def __init__(self) -> None:
        pass

    async def get_url(self, message: Message):
        msg = [message]
        if message.reply_to_message:
            msg.append(message.reply_to_message)
        url = ""
        offset = length = None
        for m in msg:
            if offset:
                break
            if m.entities:
                for entity in m.entities:
                    if entity.type == MessageEntityType.URL:
                        url = m.text or m.caption
                        offset, length = entity.offset, entity.length
                        break
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
            elif m.caption_entities:
                for entity in m.caption_entities:
                    if entity.type == MessageEntityType.URL:
                        url = m.text or m.caption
                        offset, length = entity.offset, entity.length
                        break
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return url[offset : offset + length]
