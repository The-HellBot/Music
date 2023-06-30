from config import Config


class QueueDB:
    def __init__(self):
        self.queue = {}

    def put_queue(
        self,
        chat_id: int,
        user_id: int,
        duration: str,
        file: str,
        title: str,
        user: str,
        video_id: str,
        vc_type: str = "voice",
        forceplay: bool = False,
    ) -> int:
        context = {
            "chat_id": chat_id,
            "user_id": user_id,
            "duration": duration,
            "file": file,
            "title": title,
            "user": user,
            "video_id": video_id,
            "vc_type": vc_type,
            "played": 0,
        }
        if forceplay:
            que = self.queue.get(chat_id)
            if que:
                que.insert(0, context)
            else:
                self.queue[chat_id] = []
                self.queue[chat_id].append(context)
        else:
            try:
                self.queue[chat_id].append(context)
            except KeyError:
                self.queue[chat_id] = []
                self.queue[chat_id].append(context)
        try:
            Config.CACHE[chat_id].append(file)
        except KeyError:
            Config.CACHE[chat_id] = []
            Config.CACHE[chat_id].append(file)

        position = len(self.queue.get(chat_id)) - 1

        return position

    def get_queue(self, chat_id: int) -> list:
        que = self.queue.get(chat_id) or []
        return que

    def rm_queue(self, chat_id: int, index: int):
        try:
            db = self.queue.get(chat_id)
            file = db[index]["file"]
            db.pop(index)
            return file
        except IndexError:
            return None

    def clear_queue(self, chat_id: int):
        try:
            self.queue[chat_id] = []
        except KeyError:
            pass

    def get_current(self, chat_id: int):
        try:
            return self.queue[chat_id][0]
        except KeyError:
            return None
        except IndexError:
            return None

    def update_duration(self, chat_id: int, seek_type: int, time: int):
        try:
            if seek_type == 0:
                self.queue[chat_id][0]["played"] -= time
            else:
                self.queue[chat_id][0]["played"] += time
        except IndexError:
            pass


Queue = QueueDB()
