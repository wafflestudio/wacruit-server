from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAttachment:
    file_name: str
    content_type: str
    content: bytes
