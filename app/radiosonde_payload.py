from pydantic import BaseModel
from typing import Optional, List


class RadiosondePayload(BaseModel):
    type: str
    station: str
    callsign: str
    latitude: float
    longitude: float
    altitude: float
    speed: float
    heading: float
    time: str
    comment: Optional[str] = None
    model: str
    freq: str
    temp: float
    frame: int
    bt: int
    humidity: float
    pressure: float
    sats: int
    batt: float
    snr: float
    fest: List[float]
    f_centre: float
    ppm: float
    subtype: str
    sdr_device_idx: str
    vel_v: float
    vel_h: float

    @property
    def location_tuple(self):
        return self.latitude, self.longitude
