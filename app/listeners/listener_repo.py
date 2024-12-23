from settings.listener_types import ListenerType

from .listener_base import ListenerBase
from .udp_listener import AsyncUDPListener
from .web_listener import AsyncWebListener


class ListenerRepo:
    repositories = {
        ListenerType.UDP: AsyncUDPListener,
        ListenerType.WEB: AsyncWebListener,
    }

    @classmethod
    def get_listener(cls, listener_type: ListenerType):
        return cls.repositories.get(listener_type, ListenerBase)
