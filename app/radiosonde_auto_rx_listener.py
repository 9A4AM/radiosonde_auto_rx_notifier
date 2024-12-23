import asyncio
import logging
from datetime import datetime, UTC, timedelta

from listeners.listener_repo import ListenerRepo
from radiosonde_payload import RadiosondePayload
from settings import Settings
from utils import Utils

logger = logging.getLogger(__name__)


class AsyncRadiosondeAutoRxListener:
    def __init__(self):
        self._settings: Settings = Settings.load_settings()
        self._sondes = {}

        self._purge_interval = 60  # How often to check for old radiosonde data (in seconds)
        self._purge_task = None  # Task to handle purging of old radiosonde data

        logger.info("AsyncRadiosondeAutoRxListener initialized.")

    async def start(self):
        logger.info("Starting AsyncRadiosondeAutoRxListener...")
        listener = ListenerRepo.get_listener(self._settings.listener_type)(self._settings, self.handle_payload_summary)

        logger.debug(f"Using listener: {listener.__class__.__name__}")

        await self._listen(listener)

    async def _listen(self, listener):
        # Start the listener
        listener_task = asyncio.create_task(listener.listen())

        # Start the purge task to remove old radiosonde data
        self._purge_task = asyncio.create_task(self.purge_old_radiosondes())

        # From here, everything happens in the callback function above.
        try:
            await listener_task
        # Catch CTRL+C nicely.
        except Exception as e:
            logger.exception(e)
        finally:
            # Close listener.
            listener.stop()
            await self.stop_purge_task()

    async def handle_payload_summary(self, model: dict | RadiosondePayload):
        """Handle a 'Payload Summary' UDP broadcast message, supplied as a dict."""
        if isinstance(model, dict):
            model = RadiosondePayload(**model)

        current_time = datetime.now(UTC)
        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        if self._sondes.get(model.callsign) is None:
            self._sondes[model.callsign] = {
                "notify": False,
                "landing_notify": False,
                "altitude": 0,
                "last_update": current_time,
                "data": model,
            }
            logger.info(f"New radiosonde detected: {model.callsign}.")

        if (
                model.is_descending
                and self._is_below_threshold(model)
                and Utils.is_within_range(home, model.location_tuple, range_km)
                and not self._sondes[model.callsign]["notify"]
        ):  # radiosonde is falling
            logger.debug(
                f"Radiosonde {model.callsign} is descending, within range, and below altitude threshold. Sending notification."
            )
            await Utils.send_threshold_notification(model)
            self._sondes[model.callsign]["notify"] = True

        elif (
                not model.is_descending
                or not self._is_below_threshold(model)
                or not Utils.is_within_range(home, model.location_tuple, range_km)
        ):
            if self._sondes[model.callsign]["notify"]:
                # Reset notify flag if conditions are not met
                logger.info(
                    f"Conditions not met for radiosonde {model.callsign}. Resetting notification flag."
                )
                self._sondes[model.callsign]["notify"] = False

        self._sondes[model.callsign]["altitude"] = model.altitude
        self._sondes[model.callsign]["last_update"] = current_time
        self._sondes[model.callsign]["data"] = model

    def _is_below_threshold(self, model: RadiosondePayload):
        return model.altitude < self._settings.notification_thresholds.altitude_meters

    async def purge_old_radiosondes(self):
        """Periodically check and purge radiosonde data older than 2 hours."""
        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        while True:
            logger.info("Purging old radiosonde data...")
            current_time = datetime.now(UTC)

            for callsign, data in self._sondes.items():
                last_updated = data.get("last_update")
                landing_notify = data.get("landing_notify")
                model = data.get("data")
                timeout = (
                    self._settings.notification_thresholds.landing_point_timeout_minutes
                )

                if (
                        last_updated
                        and timeout > 0
                        and (current_time - last_updated) > timedelta(minutes=timeout)
                        and not landing_notify
                        and self._is_below_threshold(model)
                        and Utils.is_within_range(home, model.location_tuple, range_km)
                ):
                    await Utils.send_landing_notification(model)
                    data["landing_notify"] = True

                if last_updated and (current_time - last_updated) > timedelta(hours=2):
                    del self._sondes[callsign]
                    logger.info(
                        f"Purged radiosonde data for {callsign} (older than 2 hours)."
                    )

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
