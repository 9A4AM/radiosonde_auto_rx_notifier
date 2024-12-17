from udp_listener import AsyncUDPListener
from settings import Settings
from radiosonde_payload import RadiosondePayload
from utils import Utils
import math
from datetime import datetime, UTC
import asyncio
import logging


logger = logging.getLogger(__name__)


class AsyncRadiosondeAutoRxListener:
    def __init__(self):
        self._settings = Settings.load_settings()
        self._sondes = {}

        self._purge_interval = 60  # How often to check for old sonde data (in seconds)
        self._purge_task = None  # Task to handle purging of old sonde data

        logger.info("AsyncRadiosondeAutoRxListener initialized.")


    async def start(self):
        # Instantiate the UDP listener.
        udp_listener = AsyncUDPListener(callback=self.handle_payload_summary, port=55673)

        # Start the UDP listener
        listener_task = asyncio.create_task(udp_listener.listen())

        # Start the purge task to remove old sonde data
        self._purge_task = asyncio.create_task(self.purge_old_sondes())

        # From here, everything happens in the callback function above.
        try:
            await listener_task
        # Catch CTRL+C nicely.
        except Exception as e:
            logger.exception(e)
        finally:
            # Close UDP listener.
            udp_listener.stop()
            await self.stop_purge_task()


    async def handle_payload_summary(self, packet: dict):
        ''' Handle a 'Payload Summary' UDP broadcast message, supplied as a dict. '''
        model = RadiosondePayload(**packet)

        current_time = datetime.now(UTC)
        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        if self._sondes.get(model.callsign) is None:
            self._sondes[model.callsign] = {
                "notify": False,
                "altitude": 0,
                "last_update": current_time
            }
            logger.info(f"New radiosonde detected: {model.callsign}.")
        
        if self._is_descending(model.altitude, model) and self._is_below_threshold(model.altitude, model) and Utils.is_within_range(home, model.location_tuple, range_km) and not self._sondes[model.callsign]['notify']: # sonde is falling
            await Utils.send_notification(model)
            self._sondes[model.callsign]['notify'] = True
            logger.debug(f"Radiosonde {model.callsign} is descending, within range, and below altitude threshold. Sending notification.")
        
        elif not self._is_descending(model.altitude, model) or not self._is_below_threshold(model.altitude, model) or not Utils.is_within_range(home, model.location_tuple, range_km):
            # Reset notify flag if conditions are not met
            if self._sondes[model.callsign]['notify']:
                logger.info(f"Conditions not met for radiosonde {model.callsign}. Resetting notification flag.")
                self._sondes[model.callsign]['notify'] = False

        self._sondes[model.callsign]['altitude'] = model.altitude
        self._sondes[model.callsign]['last_update'] = current_time

    def _is_descending(self, sonde_altitude: float, model: RadiosondePayload):
        return sonde_altitude < self._sondes[model.callsign]['altitude']

    def _is_below_threshold(self, sonde_altitude: float, model: RadiosondePayload):
        return sonde_altitude < self._settings.notification_thresholds.altitude_meters

    async def purge_old_sondes(self):
        """Periodically check and purge sonde data older than 2 hours."""
        while True:
            logger.info("Purging old radiosonde data...")
            current_time = datetime.now()
            to_remove = []

            for callsign, sonde_data in self._sondes.items():
                last_updated = sonde_data.get('last_updated')
                if last_updated and (current_time - last_updated) > timedelta(hours=2):
                    del self._sondes[callsign]
                    logger.info(f"Purged radiosonde data for {callsign} (older than 2 hours).")

            await asyncio.sleep(self._purge_interval)  # Wait for the next purge cycle

    async def stop_purge_task(self):
        """Stop the purge task gracefully."""
        if self._purge_task:
            logger.info("Stopping purge task.")
            self._purge_task.cancel()  # Gracefully stop the purge task
            try:
                await self._purge_task
            except asyncio.CancelledError:
                logger.info("Purge task cancelled.")
