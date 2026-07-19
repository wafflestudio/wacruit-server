from pydantic import BaseSettings

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings


class DiscordConfig(BaseSettings):
    bot_token: str = "token"
    discord_bot_token: str = ""
    discord_guild_id: str = ""

    class Config(BaseSettings.Config):
        case_sensitive = False
        env_file = settings.env_files

    def __init__(self) -> None:
        super().__init__()
        secret_manager = OCISecretManager()
        if secret_manager.is_available():
            try:
                self.bot_token = secret_manager.get_secret("bot_token")
            except Exception:
                pass
            try:
                self.discord_bot_token = secret_manager.get_secret("discord_bot_token")
            except Exception:
                pass
            try:
                self.discord_guild_id = secret_manager.get_secret("discord_guild_id")
            except Exception:
                pass


discord_config = DiscordConfig()
