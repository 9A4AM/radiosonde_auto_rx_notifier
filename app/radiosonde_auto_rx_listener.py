from udp_listener import AsyncUDPListener
from settings import Settings
from utils import Utils
import math
import asyncio


class AsyncRadiosondeAutoRxListener:
    def __init__(self):
        self._settings = Settings.load_settings()
        self._sondes = {}


    async def start(self):
        # Instantiate the UDP listener.
        udp_listener = AsyncUDPListener(callback=self.handle_payload_summary, port=55673)

        # Start the UDP listener
        listener_task = asyncio.create_task(udp_listener.listen())


        # From here, everything happens in the callback function above.
        try:
            await listener_task
        # Catch CTRL+C nicely.
        except KeyboardInterrupt:
            # Close UDP listener.
            udp_listener.close()
            print("Closing.")


    async def handle_payload_summary(self, packet: dict):
        ''' Handle a 'Payload Summary' UDP broadcast message, supplied as a dict. '''
        model = RadiosondePayload(**packet)

        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        if self._sondes.get(model.callsign) is None:
            self._sondes[model.callsign] = {
                "notify": False,
                "altitude": 0
            }
        
        if self._is_descending(model.altitude) and self._is_below_threshold(model.altitude) and Utils.is_within_range(home, model.location_tuple, range_km) and self._sondes[model.callsign]['notify']: # sonde is falling
            await Utils.send_notification(model)
            self._sondes[model.callsign]['notify'] = True
        
        elif not self._is_descending(model.altitude) or not self._is_below_threshold(model.altitude) or not Utils.is_within_range(home, model.location_tuple, range_km):
            self._sondes[model.callsign]['notify'] = False

        self._sondes[model.callsign]['altitude'] = model.altitude

    def _is_descending(self, sonde_altitude: float):
        return sonde_altitude < self._sondes[model.callsign]['altitude']

    def _is_below_threshold(self, sonde_altitude: float):
        return sonde_altitude < self._settings.notification_thresholds.altitude_meters
