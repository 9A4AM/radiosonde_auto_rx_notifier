from pydantic import BaseModel


class NotificationThresholds(BaseModel):
    distance_km: float  # Distance threshold in kilometers (e.g., send notification if radiosonde is within 20km)
    altitude_meters: float  # Altitude threshold in meters (e.g., send notification if altitude is below 10,000 meters)
