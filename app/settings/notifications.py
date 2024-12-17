from pydantic import BaseModel, Field


class Notification(BaseModel):
    url: str
    enabled: bool = True


class Notifications(BaseModel):
    services: list[Notification] = Field(default_factory=list)
