from config import Config
from Music import local_db


class Queue:
    def put_queue(
        chat_id: int,
        user_id: int,
        duration: str,
        file: str,
        title: str,
        user: str,
        video_id: str,
        vc_type: str = "voice",
        forceplay: bool = False,
    ):
        context = {
            "chat_id": chat_id,
            "user_id": user_id,
            "duration": duration,
            "file": file,
            "title": title,
            "user": user,
            "video_id": video_id,
            "vc_type": vc_type,
        }
        if forceplay:
            que = local_db.get(chat_id)
            if que:
                que.insert(0, context)
            else:
                local_db[chat_id] = []
                local_db[chat_id].append(context)
        else:
            local_db[chat_id].append(context)
        try:
            Config.CACHE[chat_id].append(file)
        except KeyError:
            Config.CACHE[chat_id] = []
            Config.CACHE[chat_id].append(file)

    def get_queue(chat_id: int):
        que = local_db.get(chat_id)
        return que

    def rm_queue(chat_id: int, index: int):
        try:
            local_db[chat_id].pop(index)
        except IndexError:
            pass

    def clear_queue(chat_id: int):
        try:
            local_db[chat_id] = []
        except KeyError:
            pass

    def get_current(chat_id: int):
        try:
            return local_db[chat_id][0]
        except KeyError:
            return None
        except IndexError:
            return None
