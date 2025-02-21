import asyncio
import json
import logging

from settings import Settings

from .listener_base import ListenerBase

logger = logging.getLogger(__name__)


class AsyncUDPListener(ListenerBase):
    """
    Asynchronous UDP Broadcast Packet Listener.
    Listens for Horus UDP broadcast packets and passes them to a callback function.
    """

    def __init__(self, settings: Settings, callback=None):
        """
        Initialize the UDP listener.
        :param callback: Function to process received packets.
        :param port: UDP port to listen on.
        """
        super().__init__(settings, callback)
        self.udp_port = self.settings.udp_broadcast.listen_port
        self.running = False

    async def _handle_packet(self, data, addr):
        """
        Handle an incoming UDP packet, parse it, and call the callback if valid.
        :param data: Raw packet data.
        :param addr: Address of the sender.
        """
        try:
            # Parse JSON data
            packet_dict = json.loads(data.decode())
            if packet_dict.get("type") == "PAYLOAD_SUMMARY":
                if self.callback:
                    await self.callback(packet_dict)  # Run callback
        except Exception as e:
            logger.exception(e)

    async def listen(self):
        """
        Start listening for incoming UDP packets asynchronously.
        """
        logger.debug(f"Listening for UDP packets on port {self.udp_port}...")
        self.running = True

        # Create the UDP server
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _UDPProtocol(self._handle_packet),
            local_addr=("0.0.0.0", self.udp_port),
        )

        try:
            while self.running:
                await asyncio.sleep(0.1)  # Prevent busy looping
        except asyncio.CancelledError:
            pass
        finally:
            logger.debug("Closing socket connection")
            transport.close()


class _UDPProtocol(asyncio.DatagramProtocol):
    """
    Internal protocol class to handle UDP packets.
    """

    def __init__(self, packet_handler):
        """
        Initialize the protocol.
        :param packet_handler: Coroutine function to handle received packets.
        """
        self.packet_handler = packet_handler

    def datagram_received(self, data, addr):
        """Handle received UDP packets."""
        asyncio.create_task(self.packet_handler(data, addr))
