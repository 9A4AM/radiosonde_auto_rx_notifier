import asyncio
import logging
from datetime import datetime, UTC

import aiohttp
from settings import Settings
from utils import Utils

from .listener_base import ListenerBase

logger = logging.getLogger(__name__)


class AsyncWebListener(ListenerBase):
    """
    Asynchronous UDP Broadcast Packet Listener.
    Listens for Horus UDP broadcast packets and passes them to a callback function.
    """

    def __init__(self, settings: Settings, callback=None):
        """
        Initialize the UDP listener.
        :param callback: Function to process received packets.
        """
        super().__init__(settings, callback)
        self.running = False

    async def _handle_packet(self, data):
        """
        Handle an incoming UDP packet, parse it, and call the callback if valid.
        :param data: Raw packet data.
        """
        try:
            # Parse JSON data
            if self.callback:
                for i in list(map(Utils.map_web_json_to_radiosonde_payload, data["features"])):
                    await self.callback(i)  # Run callback
        except Exception as e:
            logger.exception(e)

    async def _make_request(self):
        url = f"https://s1.radiosondy.info/export/export_map.php?live_map=1&_={int(datetime.now(UTC).timestamp() * 1000)}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        f"Failed to fetch data from online source. Status code: {response.status}"
                    )
                    return

                await self._handle_packet(await response.json())

    async def listen(self):
        logger.debug(f"Listening for packets...")
        self.running = True

        try:
            while self.running:
                await self._make_request()
                await asyncio.sleep(10)  # Prevent busy looping
        except asyncio.CancelledError:
            logger.info("Listener task cancelled.")
        except Exception as e:
            logger.exception(f"Unexpected error in listener", exc_info=e)
        finally:
            self.running = False
            logger.info("Listener stopped.")
