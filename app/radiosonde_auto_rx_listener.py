from udp_listener import UDPListener
from settings import Settings
from radiosonde_payload import RadiosondePayload
from utils import Utils
import math
import time


class RadiosondeAutoRxListener:
    def __init__(self):
        self._settings = Settings.load_settings()
        self._last_altitude = 0
        self._sondes = {}


    def start(self):
        # Instantiate the UDP listener.
        udp_rx = UDPListener(
            port=self._settings.udp_broadcast.listen_port,
            callback = self.handle_payload_summary
            )
        # and start it
        udp_rx.start()

        # From here, everything happens in the callback function above.
        try:
            while True:
                time.sleep(1)
        # Catch CTRL+C nicely.
        except KeyboardInterrupt:
            # Close UDP listener.
            udp_rx.close()
            print("Closing.")


    def handle_payload_summary(self, packet: dict):
        ''' Handle a 'Payload Summary' UDP broadcast message, supplied as a dict. '''
        model = RadiosondePayload(**packet)

        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        if self._sondes.get(model.callsign) is None:
            self._sondes[model.callsign] = False
        
        if self._is_descending(model.altitude) and self._is_below_threshold(model.altitude) and Utils.is_within_range(home, model.location_tuple, range_km) and self._sondes[model.callsign]: # sonde is falling
            Utils.send_notification(model)
            self._sondes[model.callsign] = True
        
        elif not self._is_descending(model.altitude) or not self._is_below_threshold(model.altitude) or not Utils.is_within_range(home, model.location_tuple, range_km):
            self._sondes[model.callsign] = False

        self._last_altitude = model.altitude

    def _is_descending(self, sonde_altitude: float):
        return sonde_altitude < self._last_altitude

    def _is_below_threshold(self, sonde_altitude: float):
        return sonde_altitude < self._settings.notification_thresholds.altitude_meters
