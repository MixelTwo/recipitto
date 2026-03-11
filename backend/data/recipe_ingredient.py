from typing import TypedDict

from bafser import Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from data import Tables, User
from data.ingredient import Ingredient
from data.recipe import Recipe


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = Tables.RecipeIngredient

    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Ingredient}.id"), primary_key=True)
    quantity: Mapped[float]
    unit: Mapped[str] = mapped_column(String(32))

    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)
    ingredient: Mapped[Ingredient] = relationship(foreign_keys=[ingredient_id], lazy="joined", init=False)

    @staticmethod
    def new(
        recipe_id: int,
        ingredient_id: int,
        quantity: float,
        unit: str,
        *,
        creator: User | None = None,
    ):
        obj = RecipeIngredient(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
        )
        Log.added(obj, creator)
        return obj

    def update(
        self,
        quantity: float | None = None,
        unit: str | None = None,
        *,
        actor: User | None = None,
    ):
        if quantity is not None:
            self.quantity = quantity
        if unit is not None:
            self.unit = unit
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, db_sess: Session, recipe_id: int) -> list["RecipeIngredient"]:
        return list(db_sess.query(cls).filter_by(recipe_id=recipe_id).all())

    @classmethod
    def get_by_recipe_and_ingredient(cls, db_sess: Session, recipe_id: int, ingredient_id: int) -> "RecipeIngredient | None":
        return db_sess.query(cls).filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()

    @classmethod
    def exists(cls, db_sess: Session, recipe_id: int, ingredient_id: int) -> bool:
        return cls.get_by_recipe_and_ingredient(db_sess, recipe_id, ingredient_id) is not None

    def get_dict(self) -> "RecipeIngredientDict":
        return {
            "recipe_id": self.recipe_id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "ingredient_name": self.ingredient.name,
        }


class RecipeIngredientDict(TypedDict):
    recipe_id: int
    ingredient_id: int
    quantity: float
    unit: str
    ingredient_name: str
