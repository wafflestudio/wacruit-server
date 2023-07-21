import enum


class S3PresignedUrlMethod(enum.StrEnum):
    GET = "get_object"
    PUT = "put_object"
    DELETE = "delete_object"
