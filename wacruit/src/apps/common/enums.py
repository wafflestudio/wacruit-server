from enum import Enum


class Language(Enum):
    C = 50  # GCC 9.2.0
    CPP = 54  # GCC 9.2.0
    JAVA = 62  # OpenJDK 13.0.1
    JAVASCRIPT = 93  # Node.js 18.15.0
    PYTHON = 92  # 3.11.2
    KOTLIN = 78  # 1.3.70
    SWIFT = 83  # 5.2.3
    # C = 100
    # CPP = 101
    # JAVA = 102
    # JAVASCRIPT = 103
    # PYTHON = 104
    # RUBY = 105
    # GO = 106
    # TYPESCRIPT = 107
    # KOTLIN = 108
    # SCALA = 109
    # SQL = 110
    # SWIFT = 111


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
    ERROR = 4

    @classmethod
    @property
    def NOT_SUBMITTED(cls):
        return 0


class CodeSubmissionResultStatus(Enum):
    RUNNING = 1
    CORRECT = 2
    WRONG = 3
    COMPILE_ERROR = 4
    RUNTIME_ERROR = 5
    TIME_LIMIT_EXCEEDED = 6
    MEMORY_LIMIT_EXCEEDED = 7
    INTERNAL_SERVER_ERROR = 8


class RecruitingType(Enum):
    ROOKIE = 1
    DESIGNER = 2
    PROGRAMMER = 3


class RecruitingApplicationStatus(Enum):
    IN_PROGRESS = 1
    ACCEPTED = 2
    REJECTED = 3


class ProjectType(Enum):
    SERVICE = 1
    STUDY = 2


class Position(Enum):
    FRONTEND = 1
    BACKEND = 2
    DESIGNER = 3
    ANDROID = 4
    IOS = 5
    # INFRA = 6
    # PM = 7
    # OPERATIONS = 8


class SeminarType(Enum):
    SPRING = 1
    FAST_API = 2
    FRONTEND = 3
    ANDROID = 4
    IOS = 5
