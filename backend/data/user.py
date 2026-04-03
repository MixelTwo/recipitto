from datetime import datetime
from typing import TypedDict

from bafser import Image, UserBase, get_datetime_now
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables


class User(UserBase):
    """Database model representing a user in the system.

    Extends the base User class from Bafser with additional fields.

    Attributes:
        reg_date: Date and time when the user registered.
        avatar_id: Optional ID of the user's avatar image.
        avatar: Relationship to the Image object (if avatar_id is set).
    """

    reg_date: Mapped[datetime] = mapped_column(init=False, default_factory=get_datetime_now)
    avatar_id: Mapped[int | None] = mapped_column(ForeignKey(f"{Tables.Image}.id"), default=None)

    avatar: Mapped[Image | None] = relationship(init=False, foreign_keys=[avatar_id])

    def __repr__(self):
        """Return a string representation of the User object.

        Returns:
            str: Representation in format '<User> [id] login'.
        """
        return f"<{self.__class__.__name__}> [{self.id}] {self.login}"

    def get_dict(self) -> "UserDict":
        """Convert the User object to a dictionary suitable for API responses.

        Returns:
            UserDict: Dictionary with keys id, name, login, roles, operations,
                reg_date, and avatar.
        """
        return {
            "id": self.id,
            "name": self.name,
            "login": self.login,
            "roles": self.get_roles_names(),
            "operations": self.get_operations(),
            "reg_date": self.reg_date.isoformat(),
            "avatar": self.avatar.get_path() if self.avatar else None,
        }


class UserDict(TypedDict):
    """Type‑hinted dictionary representing a user in API responses.

    Attributes:
        id: Unique identifier of the user.
        name: Display name of the user.
        login: Username used for authentication.
        roles: List of role names assigned to the user.
        operations: List of operation permissions the user has.
        reg_date: ISO‑formatted registration timestamp.
        avatar: Filesystem path or URL to the user's avatar image, or None.
    """

    id: int
    name: str
    login: str
    roles: list[str]
    operations: list[str]
    reg_date: str
    avatar: str | None
