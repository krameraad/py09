from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

from data_generator import SpaceStationGenerator, DataConfig


class SpaceStation(BaseModel):
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: Optional[str] = Field(default=None, max_length=200)


def main() -> None:
    def print_station(station: SpaceStation):
        print("Space Station Data Validation\n"
              "-----------------------------")
        print(
            "Valid station created:\n"
            f"ID: {station.station_id}\n"
            f"Name: {station.name}\n"
            f"Crew: {station.crew_size} people\n"
            f"Power: {station.power_level}%\n"
            f"Oxygen: {station.oxygen_level}%\n"
            f"Last maintained: {station.last_maintenance}"
        )
        if station.is_operational:
            print("Status: Operational")
        else:
            print("Status: Standby")
        if station.notes:
            print(f"Notes: {station.notes}")
        print()

    stations = SpaceStationGenerator(DataConfig()).generate_station_data()

    s1 = SpaceStation(
        station_id="ISS001",
        name="International Space Station",
        crew_size=6,
        power_level=85.5,
        oxygen_level=92.3,
        last_maintenance=datetime(2000, 2, 12))
    print_station(s1)

    s2 = SpaceStation(
        station_id="USSE",
        name="USS Enterprise",
        crew_size=20,
        power_level=100.0,
        oxygen_level=0.0,
        last_maintenance="2014-08-24",
        is_operational=False,
        notes="Not ready for production.")
    print_station(s2)

    for station in stations:
        print_station(SpaceStation(**station))

    try:
        s2 = SpaceStation(
            station_id="USSE",
            name="USS Enterprise",
            crew_size=21,
            power_level=100.0,
            oxygen_level=0.0,
            last_maintenance="2014-08-24",
            is_operational=False,
            notes="Not ready for production.")
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
