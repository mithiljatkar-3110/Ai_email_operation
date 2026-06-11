from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmailIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False)

    message_id: str = Field(..., min_length=1)
    thread_id: str = Field(..., min_length=1)
    sender: str = Field(..., min_length=1)
    subject: str
    body: str
    timestamp: datetime

    @field_validator("message_id", "thread_id", "sender", mode="before")
    @classmethod
    def reject_missing_string_fields(cls, value: object) -> str:
        if value is None:
            raise ValueError("field is required")
        if not isinstance(value, str):
            raise ValueError("must be a string")
        if not value.strip():
            raise ValueError("field cannot be empty")
        return value

    @field_validator("subject", mode="before")
    @classmethod
    def reject_empty_subject(cls, value: object) -> str:
        if value is None:
            raise ValueError("subject is required")
        if not isinstance(value, str):
            raise ValueError("subject must be a string")
        if not value:
            raise ValueError("subject cannot be empty")
        if not value.strip():
            raise ValueError("subject cannot be empty")
        return value

    @field_validator("body", mode="before")
    @classmethod
    def reject_empty_body(cls, value: object) -> str:
        if value is None:
            raise ValueError("body is required")
        if not isinstance(value, str):
            raise ValueError("body must be a string")
        if not value:
            raise ValueError("body cannot be empty")
        if not value.strip():
            raise ValueError("body cannot contain only whitespace")
        return value


class EmailResponse(BaseModel):
    job_id: UUID
    status: str = "accepted"
