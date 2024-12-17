from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude


class ListenerLocation(BaseModel):
    latitude: Latitude
    longitude: Longitude
    altitude: float

    @property
    def location_tuple(self):
        return self.latitude, self.longitude
