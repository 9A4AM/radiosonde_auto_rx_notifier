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
    async def send_notification(message_body, title):
        settings = Settings.load_settings()

        apobj = apprise.Apprise()

        for service in settings.notifications.services:
            if service.enabled:
                apobj.add(service.url)

         # notify all of the services loaded into our Apprise object.
        await asyncio.to_thread(apobj.notify, body=message_body, title='🚨 Radiosonde Alert 🚨')

    @staticmethod
    async def send_landing_notification(packet: RadiosondePayload):
        settings = Settings.load_settings()

        message_body = f"""
The radiosonde is nearing its landing site! Based on the latest telemetry data, here is a detailed update:

📍 Landing Prediction:
📍 **Landing Prediction**:
- **Location**: {packet.latitude}, {packet.longitude}
- **Last Known Altitude**: {packet.altitude} meters
- **Distance from Listener**: {round(Utils.get_distance(settings.listener_location.location_tuple, packet.location_tuple), 2)} km

📊 **Radiosonde Details**:
- **Callsign**: {packet.callsign}
- **Model**: {packet.model}
- **Frequency**: {packet.freq}
- **Battery**: {packet.batt} V
- **Last Known Speed**: {packet.vel_v} m/s



Click the link to view the location on Google Maps: [Google Maps](https://www.google.com/maps?q={packet.latitude},{packet.longitude})

💡 Recommendation:
If you're planning retrieval, ensure you have the necessary equipment and safety precautions. The area might be remote or challenging to access.
"""

        # notify all of the services loaded into our Apprise object.
        await Utils.send_notification(message_body, '🚨 Radiosonde Alert 🚨')


    @staticmethod
    async def send_threshold_notification(packet: RadiosondePayload):
        settings = Settings.load_settings()

        message_body = f"""
The radiosonde is within {settings.notification_thresholds.distance_km} km and below {settings.notification_thresholds.altitude_meters} meters altitude.

📍 **Landing Prediction**:
- **Location**: {packet.latitude}, {packet.longitude}
- **Last Known Altitude**: {packet.altitude} meters
- **Distance from Listener**: {round(Utils.get_distance(settings.listener_location.location_tuple, packet.location_tuple), 2)} km

📊 **Radiosonde Details**:
- **Callsign**: {packet.callsign}
- **Model**: {packet.model}
- **Frequency**: {packet.freq}
- **Battery**: {packet.batt} V
- **Last Known Speed**: {packet.vel_v} m/s

Click the link to view the location on Google Maps: [Google Maps](https://www.google.com/maps?q={packet.latitude},{packet.longitude})
"""


        await Utils.send_notification(message_body, '🚨 Radiosonde Alert 🚨')
