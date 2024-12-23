from pathlib import Path

from pydantic import BaseModel
from yaml import safe_load, dump

from .listener_location import ListenerLocation
from .listener_types import ListenerType
from .notification_thresholds import NotificationThresholds
from .notifications import Notifications
from .udp_broadcast import UDPBroadcast


class Settings(BaseModel):
    listener_location: ListenerLocation
    notification_thresholds: NotificationThresholds
    udp_broadcast: UDPBroadcast
    listener_type: ListenerType
    notifications: Notifications

    @classmethod
    def create_settings_file(cls, settings_file_path):
        settings = cls.get_default_settings()

        with open(settings_file_path, "w") as settings_file:
            dump(settings.model_dump(mode="json"), settings_file, indent=2)

        return settings

    @classmethod
    def load_settings(cls):
        settings_file_path = Path(__file__).parent.parent.parent / "data/config.yml"

        if not settings_file_path.exists():
            return Settings.create_settings_file(settings_file_path)

        with open(settings_file_path, "r") as settings_file:
            return cls(**safe_load(settings_file))

    @classmethod
    def get_default_settings(cls):
        data = {
            "listener_location": {"latitude": 0, "longitude": 0, "altitude": 0},
            "notification_thresholds": {"distance_km": 20, "altitude_meters": 1000},
            "udp_broadcast": {"enabled": True, "listen_port": 55673},
            "listener_type": "UDP",
            "notifications": {"services": [{"url": "", "enabled": True}]},
        }

        return cls(**data)
