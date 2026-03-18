from datetime import datetime
from typing import Self
from enum import Enum, auto

from pydantic import BaseModel, Field, ValidationError, model_validator

from data_generator import CrewMissionGenerator, DataConfig


class Rank(Enum):
    cadet = auto()
    officer = auto()
    lieutenant = auto()
    captain = auto()
    commander = auto()


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def check(self) -> Self:
        if self.mission_id[0] != 'M':
            raise ValueError("Mission ID doesn't start with 'M'.")

        if not [x for x in self.crew
                if x.rank == Rank.captain or x.rank == Rank.commander]:
            raise ValueError(
                "Missing at least one captain or commander.")

        if self.duration_days > 365:
            experienced_crew = [x for x in self.crew
                                if x.years_experience >= 5]
            if len(experienced_crew) / len(self.crew) < 0.5:
                raise ValueError("Not enough experienced crew "
                                 "(5+ years, threshold 50%).")

        if [x for x in self.crew if not x.is_active]:
            raise ValueError("Not all crew members are active.")

        return self


def main() -> None:
    def print_mission(mission: SpaceMission):
        def print_crewmember(crewmember: CrewMember):
            print(f"- {crewmember.name} ({crewmember.rank.name}) "
                  f"- {crewmember.specialization}")

        print("Space Mission Crew Validation\n"
              "-----------------------------")
        print(
            f"Mission: {mission.mission_name}\n"
            f"ID: {mission.mission_id}\n"
            f"Destination: {mission.destination}\n"
            f"Duration: {mission.duration_days} days\n"
            f"Budget: ${mission.budget_millions}M\n"
            f"Crew size: {len(mission.crew)}\n"
            "Crew members:"
        )
        for crewmember in mission.crew:
            print_crewmember(crewmember)
        print()

    missions = CrewMissionGenerator(DataConfig()).generate_mission_data()
    for mission in missions:
        for crewmember in mission["crew"]:
            crewmember["rank"] = Rank[crewmember["rank"]]
        mission["crew"] = [CrewMember(**x) for x in mission["crew"]]
        print_mission(SpaceMission(**mission))

    try:  # Specific report
        crew: list[CrewMember] = []
        crew.append(CrewMember(
            member_id="kaas",
            name="Sarah Connor",
            rank=Rank.commander,
            age=30,
            specialization="Mission Command",
            years_experience=20,
            # is_active=False
        ))
        crew.append(CrewMember(
            member_id="kaas",
            name="John Smith",
            rank=Rank.lieutenant,
            age=30,
            specialization="Navigation",
            years_experience=20,
            # is_active=False
        ))
        crew.append(CrewMember(
            member_id="kaas",
            name="Alice Johnson",
            rank=Rank.officer,
            age=30,
            specialization="Engineering",
            years_experience=20,
            # is_active=False
        ))
        m = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date="2024-01-01",
            duration_days=900,
            crew=crew,
            budget_millions=2500.0)
        print_mission(m)
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
