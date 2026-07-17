from pathlib import Path
from typing import Literal

from pydantic import BaseSettings

ROOT_PATH = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    env: Literal["dev", "prod", "local", "test"] = "local"
    oci_region: str = "ap-chuncheon-1"
    sql_echo: bool = False
    TOKEN_SECRET: str = "secret"
    bot_token: str = "token"
    discord_bot_token: str = ""
    discord_guild_id: str = ""

    @property
    def oci_secret_ocid(self) -> str | None:
        s = "ocid1.vaultsecret.oc1.ap-chuncheon-1."
        if self.env == "dev":
            return s + "amaaaaaat2m5lbqamvh6nypm72o2om2bk77d3gev3zsryfwt7idsoi7fccxa"
        if self.env == "prod":
            return s + "amaaaaaat2m5lbqad2qlgakgqhnym4ixoai7qywmfx2oft3zspsrxfgcic4q"
        return None

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @property
    def is_local(self) -> bool:
        return self.env == "local"

    @property
    def is_test(self) -> bool:
        return self.env == "test"

    @property
    def env_files(self) -> tuple[Path, ...]:
        if self.env in ["local", "test"]:
            return (ROOT_PATH / f".env.{self.env}",)

        return (
            ROOT_PATH / f".env.{self.env}",
            ROOT_PATH / f".env.{self.env}.local",
        )


settings = Settings()
