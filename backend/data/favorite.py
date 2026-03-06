from datetime import datetime
from typing import TypedDict

from bafser import Log, SqlAlchemyBase, get_datetime_now
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Favorite(SqlAlchemyBase):
    __tablename__ = Tables.Favorite

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(init=False, default=get_datetime_now)

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        *,
        creator: User | None = None,
    ):
        obj = Favorite(
            user_id=user_id,
            recipe_id=recipe_id,
        )
        Log.added(obj, creator)
        return obj

    def get_dict(self) -> "FavoriteDict":
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "added_at": self.added_at.isoformat(),
        }


class FavoriteDict(TypedDict):
    user_id: int
    recipe_id: int
    added_at: str
