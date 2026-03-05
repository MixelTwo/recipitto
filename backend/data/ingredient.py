from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from data import Tables, User
from utils import normalize_for_search


class Ingredient(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.Ingredient
    name: Mapped[str] = mapped_column(String(64))
    name_normalized: Mapped[str] = mapped_column(String(64), init=False)
    category_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.IngredientCategory}.id"))

    category: Mapped[IngredientCategory] = relationship(foreign_keys=[category_id], lazy="joined", init=False)

    @validates("name")
    def update_name_normalized(self, key: str, value: str):
        self.name_normalized = normalize_for_search(value)
        return value

    @staticmethod
    def new(name: str, category_id: int, *, creator: User | None = None):
        obj = Ingredient(name=name, category_id=category_id)
        Log.added(obj, creator)
        return obj

    def update(self, name: str | None, category_id: int | None, *, actor: User | None = None):
        if name is not None:
            self.name = name
        if category_id is not None:
            self.category_id = category_id

        Log.updated(self, actor)

    def get_dict(self) -> "IngredientDict":
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
        }


class IngredientDict(TypedDict):
    id: int
    name: str
    category: str
