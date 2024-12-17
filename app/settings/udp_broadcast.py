from pydantic import BaseModel


class UDPBroadcast(BaseModel):
    enabled: bool = True
    listen_port: int = 55673
