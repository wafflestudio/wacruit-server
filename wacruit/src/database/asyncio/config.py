from wacruit.src.database.config import DBConfig


class AsyncDBConfig(DBConfig):
    @property
    def backend(self) -> str:
        return "aiomysql"


db_config = AsyncDBConfig()
