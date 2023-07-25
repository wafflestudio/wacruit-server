from enum import Enum


class Language(Enum):
    C = 100
    CPP = 101
    JAVA = 102
    JAVASCRIPT = 103
    PYTHON = 104
    RUBY = 105
    GO = 106
    TYPESCRIPT = 107
    KOTLIN = 108
    SCALA = 109
    SQL = 110
    SWIFT = 111


class JudgeSubmissionStatus(Enum):
    IN_QUEUE = 1
    PROCESSING = 2
    ACCEPTED = 3
    WRONG_ANSWER = 4
    TIME_LIMIT_EXCEEDED = 5
    COMPILATION_ERROR = 6
    RUNTIME_ERROR_SIGSEGV = 7
    RUNTIME_ERROR_SIGXFSZ = 8
    RUNTIME_ERROR_SIGFPE = 9
    RUNTIME_ERROR_SIGABRT = 10
    RUNTIME_ERROR_NZEC = 11
    RUNTIME_ERROR_OTHER = 12
    INTERNAL_ERROR = 13
    EXEC_FORMAT_ERROR = 14


class CodeSubmissionStatus(Enum):
    RUNNING = 1
    SOLVED = 2
    WRONG = 3

    @classmethod
    @property
    def NOT_SUBMITTED(cls):
        return 0
