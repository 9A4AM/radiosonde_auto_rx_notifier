from abc import ABC, abstractmethod
from settings import Settings


class ListenerBase(ABC):
    def __init__(self, settings: Settings, callback=None):
        self.settings = settings
        self.callback = callback

    @abstractmethod
    async def listen(self):
        """Start the listener."""
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """Stop the listener."""
        raise NotImplementedError
