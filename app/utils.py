import apprise
from geopy import distance
import asyncio

from radiosonde_payload import RadiosondePayload
from settings import Settings


class Utils:
    @staticmethod
    def get_distance(base_coordinates, sonde_coordinates):
        return distance.distance(base_coordinates, sonde_coordinates).km

    @staticmethod
    def is_within_range(base_coordinates, sonde_coordinates, range_km):
        distance = Utils.get_distance(base_coordinates, sonde_coordinates)
        return distance <= range_km

    @staticmethod
    async def send_notification(packet: RadiosondePayload):
        settings = Settings.load_settings()

        apobj = apprise.Apprise()

        for service in settings.notifications.services:
            if service.enabled:
                apobj.add(service.url)
        
        message_body = f"""
Callsign: {packet.callsign}
Location: {packet.latitude}, {packet.longitude}
Altitude: {packet.altitude} meters
Distance from Listener: {round(Utils.get_distance(settings.listener_location.location_tuple, packet.location_tuple), 2)} km

The radiosonde is within {settings.notification_thresholds.distance_km} km and below {settings.notification_thresholds.altitude_meters} meters altitude.
Click the link to view the location on Google Maps: https://www.google.com/maps?q={packet.latitude},{packet.longitude}
"""

        # notify all of the services loaded into our Apprise object.
        await asyncio.to_thread(apobj.notify, body=message_body, title='🚨 Radiosonde Alert 🚨')
