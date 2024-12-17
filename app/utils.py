import apprise
import asyncio

from settings import Settings


class Utils:
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Radius of Earth in kilometers
        radius = 6371.0
        
        # Distance in kilometers
        distance = radius * c
        return distance

    @staticmethod
    def is_within_range(base_coordinates, sonde_coordinates, range_km):
        distance = Utils.haversine(*base_coordinates, *sonde_coordinates)
        return distance <= range_km

    @staticmethod
    async def send_notification(packet: dict):
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
        await asyncio.to_thread(apobj.notify, body=message_body, title='🚨 Radiosonde Alert 🚨')
