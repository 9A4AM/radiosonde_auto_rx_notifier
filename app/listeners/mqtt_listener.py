import asyncio
import logging
import json

import aiomqtt
from settings import Settings
from utils import Utils

from .listener_base import ListenerBase

logger = logging.getLogger(__name__)


class AsyncMqttListener(ListenerBase):
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
        self.task = None

    async def _handle_packet(self, data):
        """
        Handle an incoming UDP packet, parse it, and call the callback if valid.
        :param data: Raw packet data.
        """
        try:
            data = json.loads(data.payload)

            # Parse JSON data
            if self.callback:
                await self.callback(Utils.map_mqtt_json_to_radiosonde_payload(data))  # Run callback
        except Exception as e:
            logger.exception(e)

    async def listen(self):
        logger.debug(f"Listening for packets...")
        mqtt_client = aiomqtt.Client(
            "ws-reader.v2.sondehub.org",
            port=443,
            transport="websockets",
            tls_params=aiomqtt.TLSParameters()
        )
        interval = 5

        try:
            while True:
                try:
                    async with mqtt_client as client:
                        await client.subscribe("sondes/#")
                        async for message in client.messages:
                            await self._handle_packet(message)
                except aiomqtt.MqttError:
                    logger.warning(f"Connection lost; Reconnecting in {interval} seconds ...")
                    await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Listener task cancelled.")
        except Exception as e:
            logger.exception(f"Unexpected error in listener", exc_info=e)
        finally:
            logger.info("Listener stopped.")
