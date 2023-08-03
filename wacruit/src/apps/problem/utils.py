from decimal import Decimal

from pydantic import BaseModel

from wacruit.src.apps.common.enums import Language


class Factor(BaseModel):
    multiply: int
    increment: int


class Handi(BaseModel):
    time: Factor
    memory: Factor


handi_map = {
    Language.C: Handi(
        time=Factor(multiply=1, increment=0),
        memory=Factor(multiply=1, increment=1500 + 0),
    ),
    Language.CPP: Handi(
        time=Factor(multiply=1, increment=0),
        memory=Factor(multiply=1, increment=2500 + 0),
    ),
    Language.PYTHON: Handi(
        time=Factor(multiply=3, increment=2),
        memory=Factor(multiply=2, increment=3500 + 32000),
    ),
    Language.JAVA: Handi(
        time=Factor(multiply=2, increment=1),
        memory=Factor(multiply=2, increment=10500 + 16000),
    ),
    Language.KOTLIN: Handi(
        time=Factor(multiply=2, increment=1),
        memory=Factor(multiply=2, increment=10500 + 16000),
    ),
    Language.SWIFT: Handi(
        time=Factor(multiply=2, increment=1),
        memory=Factor(multiply=2, increment=10500 + 16000),
    ),
    Language.JAVASCRIPT: Handi(
        time=Factor(multiply=3, increment=2),
        memory=Factor(multiply=2, increment=8000 + 2000),
    ),
}


def time_handi(time: float, language: Language) -> float:
    handi = handi_map[language]
    return time * handi.time.multiply + handi.time.increment


def memory_handi(memory: int, language: Language) -> int:
    handi = handi_map[language]
    return memory * handi.memory.multiply + handi.memory.increment
