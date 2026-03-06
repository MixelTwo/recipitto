from typing import TypedDict

from bafser import Image, Log, ObjMixin, SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class RecipeImage(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.RecipeImage

    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"))
    image_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Image}.id"))

    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)
    image: Mapped[Image] = relationship(foreign_keys=[image_id], lazy="joined", init=False)

    @staticmethod
    def new(
        recipe_id: int,
        image_id: int,
        *,
        creator: User | None = None,
    ):
        obj = RecipeImage(
            recipe_id=recipe_id,
            image_id=image_id,
        )
        Log.added(obj, creator)
        return obj

    def get_dict(self) -> "RecipeImageDict":
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "image_id": self.image_id,
            "image_path": self.image.get_path(),
        }


class RecipeImageDict(TypedDict):
    id: int
    recipe_id: int
    image_id: int
    image_path: str
