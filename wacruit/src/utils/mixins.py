from logging import getLogger
from logging import Logger


class LoggingMixin:
    __logger: Logger

    @property
    def logger(self) -> Logger:
        try:
            return self.__logger
        except AttributeError:
            self.__logger = getLogger(
                f"{self.__class__.__module__}:{self.__class__.__name__}"
            )
            return self.__logger
