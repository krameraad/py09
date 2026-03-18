from datetime import datetime
from typing import Optional, Self
from enum import Enum, auto

from pydantic import BaseModel, Field, ValidationError, model_validator

from data_generator import AlienContactGenerator, DataConfig


class ContactType(Enum):
    radio = auto()
    visual = auto()
    physical = auto()
    telepathic = auto()


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode='after')
    def check(self) -> Self:
        if self.contact_id[:2] != "AC":
            raise ValueError("Contact ID doesn't start with 'AC'.")
        if self.contact_type == ContactType.physical and not self.is_verified:
            raise ValueError("Physical contact report is not verified.")
        if self.contact_type == ContactType.telepathic \
                and self.witness_count < 3:
            raise ValueError("Telepathic contact has less than 3 witnesses.")
        if self.signal_strength > 7.0 and self.message_received is None:
            raise ValueError("Strong signal doesn't include message.")
        return self


def main() -> None:
    def print_contact(contact: AlienContact):
        print("Alien Contact Log Validation\n"
              "-----------------------------")
        print(
            f"ID: {contact.contact_id}\n"
            f"Type: {contact.contact_type.name}\n"
            f"Location: {contact.location}\n"
            f"Signal: {contact.signal_strength}/10\n"
            f"Duration: {contact.duration_minutes} minutes\n"
            f"Witnesses: {contact.witness_count}"
        )
        if contact.message_received:
            print(f"Message: '{contact.message_received}'")
        if contact.is_verified:
            print("~ Verified ~")
        print()

    contacts = AlienContactGenerator(DataConfig()).generate_contact_data()

    for contact in contacts:
        new_contact_type = ContactType[contact["contact_type"]]
        contact.update({"contact_type": new_contact_type})
        print_contact(AlienContact(**contact))

    try:  # Valid report
        a = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2025-01-01",
            contact_type=ContactType.radio,
            location="Area 51, Nevada",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli")
        print_contact(a)
    except ValidationError as e:
        print(e)

    try:  # Contact ID must start with "AC" (Alien Contact)
        a = AlienContact(
            contact_id="AD_2024_001",
            timestamp="2025-01-01",
            contact_type=ContactType.radio,
            location="Area 51, Nevada",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli")
        print_contact(a)
    except ValidationError as e:
        print(e)

    try:  # Physical contact reports must be verified
        a = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2025-01-01",
            contact_type=ContactType.physical,
            location="Area 51, Nevada",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli")
        print_contact(a)
    except ValidationError as e:
        print(e)

    try:  # Telepathic contact requires at least 3 witnesses
        a = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2025-01-01",
            contact_type=ContactType.telepathic,
            location="Area 51, Nevada",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=2,
            message_received="Greetings from Zeta Reticuli")
        print_contact(a)
    except ValidationError as e:
        print(e)

    try:  # Strong signals (> 7.0) should include received messages
        a = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2025-01-01",
            contact_type=ContactType.radio,
            location="Area 51, Nevada",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5)
        print_contact(a)
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
