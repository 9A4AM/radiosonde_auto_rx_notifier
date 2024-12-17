from pydantic import BaseModel


class ListenerLocation(BaseModel):
    latitude: float
    longitude: float
    altitude: float

    @property
    def location_tuple(self):
        return self.latitude, self.longitude
