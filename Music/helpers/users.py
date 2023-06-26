from .strings import TEXTS


class UserModel:
    def __init__(self) -> None:
        self.profile = TEXTS.PROFILE
        self.stats = TEXTS.STATS

    def get_profile_text(self, context: dict) -> str:
        return self.profile.format(
            self.get_user_level_symbol(context["songs_played"]),
            context["mention"],
            context["id"],
            self.get_user_level(context["songs_played"]),
            context["songs_played"],
            context["join_date"],
        )

    def get_user_level(self, songs_played: int) -> str:
        if songs_played < 20:
            return "Novice"
        elif songs_played < 40:
            return "Beginner"
        elif songs_played < 80:
            return "Intermediate"
        elif songs_played < 160:
            return "Advanced"
        elif songs_played < 320:
            return "Expert"
        else:
            return "Master"

    def get_user_level_symbol(self, songs_played: int) -> str:
        if songs_played < 20:
            return "☆"
        elif songs_played < 40:
            return "★"
        elif songs_played < 80:
            return "✭"
        elif songs_played < 160:
            return "⍟"
        elif songs_played < 320:
            return "❂"
        else:
            return "❉"

    def get_stats_text(self, context: dict) -> str:
        (
            users,
            chats,
            gbans,
            blocked,
            songs,
            active,
            core,
            cpu,
            disk,
            ram,
            uptime,
            mention,
        ) = context.values()
        return self.stats.format(
            users, chats, gbans, blocked, songs, active, core, cpu, disk, ram, uptime, mention
        )


MusicUser = UserModel()
