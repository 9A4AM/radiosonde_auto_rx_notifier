import apprise
from geopy import distance

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
    def send_notification(packet: dict):
        settings = Settings.load_settings()

        apobj = apprise.Apprise()

        for service in settings.notifications.services:
            if service.enabled:
                apobj.add(service.url)
        
        message_body = f"""
Callsign: TEST123
Location: 40.7128, -74.0060
Altitude: 500 meters
Distance from Listener: 15.0 km
Timestamp: 2024-12-17 12:30:00

The radiosonde is within 20 km and below 1000 meters altitude.
Click the link to view the location on Google Maps: https://www.google.com/maps?q=40.7128,-74.0060
"""

        # notify all of the services loaded into our Apprise object.
        apobj.notify(
            body=message_body,
            title='🚨 Radiosonde Alert 🚨',
        )
