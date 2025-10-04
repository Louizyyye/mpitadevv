from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# ==========================================================
#                     LOG SCHEMAS
# ==========================================================

class LogBase(BaseModel):
    """
    Base schema for logs.
    """
    user_id: Optional[int] = Field(None, description="ID of the user associated with the log")
    level: str = Field(..., description="Log level: info | warning | error")
    message: str = Field(..., description="Log message content")


class LogCreate(LogBase):
    """
    Schema for creating a new log entry.
    """
    pass  # Inherits all fields from LogBase


class LogResponse(LogBase):
    """
    Schema returned when querying logs.
    """
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
