import aiohttp
import logging
import asyncio
from datetime import datetime, UTC

from utils import Utils


logger = logging.getLogger(__name__)


class AsyncWebListener:
    """
    Asynchronous UDP Broadcast Packet Listener.
    Listens for Horus UDP broadcast packets and passes them to a callback function.
    """

    def __init__(self, callback=None):
        """
        Initialize the UDP listener.
        :param callback: Function to process received packets.
        """
        self.callback = callback
        self.running = False

    async def handle_packet(self, data):
        """
        Handle an incoming UDP packet, parse it, and call the callback if valid.
        :param data: Raw packet data.
        """
        try:
            # Parse JSON data
            if self.callback:
                for i in list(map(Utils.map_json_to_radiosonde_payload, data["features"])):
                    await self.callback(i)  # Run callback
        except Exception as e:
            logger.exception(e)
    
    async def make_request(self):
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

                await self.handle_packet(await response.json())

    async def listen(self):
        """
        Start listening for incoming UDP packets asynchronously.
        """
        logger.debug(f"Listening for packets...")
        self.running = True

        # Create the UDP server
        loop = asyncio.get_running_loop()

        try:
            while self.running:
                await self.make_request()
                await asyncio.sleep(10)  # Prevent busy looping
        except asyncio.CancelledError:
            pass
        finally:
            pass

    def stop(self):
        """Stop the listener."""
        self.running = False
