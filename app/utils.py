import apprise
import asyncio
from geopy import distance

from radiosonde_payload import RadiosondePayload
from settings import Settings


class Utils:
    @staticmethod
    def get_distance(listener_coordinates, radiosonde_coordinates):
        return distance.distance(listener_coordinates, radiosonde_coordinates).km

    @staticmethod
    def is_within_range(listener_coordinates, radiosonde_coordinates, range_km):
        distance_from_listener = Utils.get_distance(listener_coordinates, radiosonde_coordinates)
        return distance_from_listener <= range_km

    @staticmethod
    async def send_notification(message_body, title):
        settings = Settings.load_settings()

        notifier = apprise.Apprise()

        for service in settings.notifications.services:
            if service.enabled:
                notifier.add(service.url)

        # notify all the services loaded into our Apprise object.
        asyncio.create_task(
            notifier.async_notify(body=message_body, title=title)
        )

    @staticmethod
    def map_mqtt_json_to_radiosonde_payload(json_payload: dict):
        """Map "sondehub" MQTT data to a RadiosondePayload object"""
        return RadiosondePayload(
            callsign=json_payload.get("serial", ""),
            model=json_payload.get("type", ""),
            freq=str(json_payload.get("frequency", "0.0")) + "MHz",
            batt=json_payload.get("batt", -1),
            vel_v=json_payload.get("vel_v", 0.0),
            vel_h=json_payload.get("vel_h", 0.0),
            altitude=int(json_payload.get("alt", 0)),
            latitude=json_payload.get("lat", 0.0),
            longitude=json_payload.get("lon", 0.0),
            sdr_device_idx="0",
            subtype=json_payload.get("subtype", ""),
            ppm=0,
            f_centre=0.0,
            fest=[],
            snr=json_payload.get("rssi", 0),
            sats=json_payload.get("sats", 0),
            pressure=json_payload.get("pressure", 0),
            humidity=json_payload.get("humidity", 0),
            bt=json_payload.get("burst_timer", 0),
            frame=json_payload.get("frame", 0),
            temp=json_payload.get("temp", 0),
            time=json_payload.get("datetime", ""),
            heading=json_payload.get("heading", 0.0),
            speed=json_payload.get("vel_h", 0.0),
            station=json_payload.get("uploader_callsign", ""),
            type=""
        )

    @staticmethod
    def map_web_json_to_radiosonde_payload(json_payload: dict):
        """Map "radiosondy" data to a RadiosondePayload object
        """
        return RadiosondePayload(
            callsign=json_payload.get("properties").get("id", ""),
            model=json_payload.get("properties").get("type", ""),
            freq=json_payload.get("properties").get("frequency", "0.0"),
            batt=-1,
            vel_v=float(json_payload.get("properties").get("climbing", "0.0").replace(" m/s", "")),
            vel_h=float(json_payload.get("properties").get("speed", "0.0").replace(" km/h", "")) / 3.6,
            altitude=int(json_payload.get("properties").get("altitude", "0").replace(" m", "")),
            latitude=float(json_payload.get("properties").get("latitude", "0.0")),
            longitude=float(json_payload.get("properties").get("longitude", "0.0")),
            sdr_device_idx="0",
            subtype="",
            ppm=0,
            f_centre=0.0,
            fest=[],
            snr=0,
            sats=0,
            pressure=0,
            humidity=0,
            bt=0,
            frame=0,
            temp=0,
            time="",
            heading=float(json_payload.get("properties").get("course", "0.0").replace(" °", "")),
            speed=float(json_payload.get("properties").get("speed", "0.0").replace(" km/h", "")),
            station="",
            type=""
        )

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

Click the link to view the location on [Google Maps](https://www.google.com/maps?q={packet.latitude},{packet.longitude})

💡 Recommendation:
If you're planning retrieval, ensure you have the necessary equipment and safety precautions. The area might be remote or challenging to access.
"""

        await Utils.send_notification(message_body, "🚨 Radiosonde Alert 🚨")

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

Click the link to view the location on [Google Maps](https://www.google.com/maps?q={packet.latitude},{packet.longitude})
"""

        await Utils.send_notification(message_body, "🚨 Radiosonde Alert 🚨")
