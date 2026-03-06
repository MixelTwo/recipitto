from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from data import Tables, User
from utils import normalize_for_search


class IngredientCategory(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.IngredientCategory
    name: Mapped[str] = mapped_column(String(64))
    name_normalized: Mapped[str] = mapped_column(String(64), init=False)

    @validates("name")
    def update_name_normalized(self, key: str, value: str):
        self.name_normalized = normalize_for_search(value)
        return value

    @staticmethod
    def new(name: str, *, creator: User | None = None):
        obj = IngredientCategory(name=name)
        Log.added(obj, creator)
        return obj

    def update(self, name: str | None, *, actor: User | None = None):
        if name is not None:
            self.name = name
        Log.updated(self, actor)

    def get_dict(self) -> "IngredientCategoryDict":
        return {
            "id": self.id,
            "name": self.name,
        }


class IngredientCategoryDict(TypedDict):
    id: int
    name: str
