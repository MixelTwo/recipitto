from typing import TypedDict

from bafser import Image, Log, ObjMixin, SqlAlchemyBase, get_db_session
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class RecipeStep(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.RecipeStep

    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"))
    step_number: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    image_id: Mapped[int | None] = mapped_column(ForeignKey(f"{Tables.Image}.id"), default=None)

    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)
    image: Mapped[Image | None] = relationship(foreign_keys=[image_id], lazy="joined", init=False)

    @staticmethod
    def new(
        recipe_id: int,
        step_number: int,
        text: str,
        image_id: int | None = None,
        *,
        creator: User | None = None,
    ):
        obj = RecipeStep(
            recipe_id=recipe_id,
            step_number=step_number,
            text=text,
            image_id=image_id,
        )
        Log.added(obj, creator)
        return obj

    def update(
        self,
        step_number: int | None = None,
        text: str | None = None,
        image_id: int | None = None,
        *,
        actor: User | None = None,
    ):
        if step_number is not None:
            self.step_number = step_number
        if text is not None:
            self.text = text
        if image_id is not None:
            self.image_id = image_id
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["RecipeStep"]:
        db_sess = db_sess or get_db_session()
        return list(db_sess.query(cls).filter_by(recipe_id=recipe_id).all())

    def get_dict(self) -> "RecipeStepDict":
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "step_number": self.step_number,
            "text": self.text,
            "image": self.image.get_path() if self.image else None,
        }


class RecipeStepDict(TypedDict):
    id: int
    recipe_id: int
    step_number: int
    text: str
    image: str | None
