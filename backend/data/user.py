from datetime import datetime

from bafser import Image, UserBase, get_datetime_now
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables


class User(UserBase):
    reg_date: Mapped[datetime] = mapped_column(init=False, default=get_datetime_now)
    avatar_id: Mapped[int | None] = mapped_column(ForeignKey(f"{Tables.Image}.id"), default=None)

    avatar: Mapped[Image | None] = relationship(init=False, foreign_keys=[avatar_id])

    def __repr__(self):
        return f"<{self.__class__.__name__}> [{self.id}] {self.login}"
