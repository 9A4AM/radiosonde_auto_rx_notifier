from udp_listener import UDPListener
from settings import Settings
from utils import Utils
import math
import time


class RadiosondeAutoRxListener:
    def __init__(self):
        self._settings = Settings.load_settings()
        self._last_altitude = 0
        self._notification_send = False
        self.sondes = {}


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
        range_km = self._settings.notification_thresholds.distance_km
        home = self._settings.listener_location.location_tuple

        sonde_position = (packet.get('latitude', 0), packet.get('longitude', 0))
        sonde_altitude = packet.get('altitude', 0)
        
        if self._is_descending(sonde_altitude) and self._is_below_threshold(sonde_altitude) and Utils.is_within_range(home, sonde_position, range_km) and self._notification_send: # sonde is falling
            Utils.send_notification(packet)
            self._notification_send = True
        
        elif not self._is_descending(sonde_altitude) or not self._is_below_threshold(sonde_altitude) or not Utils.is_within_range(home, sonde_position, range_km):
            self._notification_send = False

        self.last_altitude = sonde_altitude

    def _is_descending(self, sonde_altitude: float):
        return sonde_altitude < self.last_altitude

    def _is_below_threshold(self, sonde_altitude: float):
        return sonde_altitude < self._settings.notification_thresholds.altitude_meters
