from typing import TypedDict

from bafser import Log, SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Rating(SqlAlchemyBase):
    __tablename__ = Tables.Rating

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"), primary_key=True)
    rating: Mapped[int]  # 1-5

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        rating: int,
        *,
        creator: User | None = None,
    ):
        obj = Rating(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=rating,
        )
        Log.added(obj, creator)
        return obj

    def update(
        self,
        rating: int | None = None,
        *,
        actor: User | None = None,
    ):
        if rating is not None:
            self.rating = rating
        Log.updated(self, actor)

    def get_dict(self) -> "RatingDict":
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "rating": self.rating,
        }


class RatingDict(TypedDict):
    user_id: int
    recipe_id: int
    rating: int
