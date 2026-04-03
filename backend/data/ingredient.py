from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from data import IngredientCategory, Tables, User
from utils import normalize_for_search


class Ingredient(SqlAlchemyBase, ObjMixin):
    """Database model representing an ingredient.

    Attributes:
        name: Display name of the ingredient (max 64 characters).
        name_normalized: Normalized version of the name for search purposes.
        category_id: ID of the ingredient category this ingredient belongs to.
        category: Relationship to the IngredientCategory object.
    """

    __tablename__ = Tables.Ingredient
    name: Mapped[str] = mapped_column(String(64))
    name_normalized: Mapped[str] = mapped_column(String(64), init=False)
    category_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.IngredientCategory}.id"))

    category: Mapped[IngredientCategory] = relationship(foreign_keys=[category_id], lazy="joined", init=False)

    @validates("name")
    def update_name_normalized(self, key: str, value: str) -> str:
        """SQLAlchemy validator that updates the normalized name when name changes.

        Args:
            key: Field name being validated (always "name").
            value: New value for the name field.

        Returns:
            str: The original value (unchanged).
        """
        self.name_normalized = normalize_for_search(value)
        return value

    @staticmethod
    def new(name: str, category_id: int, *, creator: User | None = None) -> "Ingredient":
        """Create a new Ingredient record.

        Args:
            name: Display name for the ingredient.
            category_id: ID of the ingredient category.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.

        Returns:
            Ingredient: The newly created Ingredient object.
        """
        obj = Ingredient(name=name, category_id=category_id)
        Log.added(obj, creator)
        return obj

    def update(self, name: str | None, category_id: int | None, *, actor: User | None = None):
        """Update the ingredient's fields.

        Args:
            name: New name for the ingredient, or None to keep the current value.
            category_id: New category ID, or None to keep the current value.
            actor: Optional User object representing who performed the update
                (for logging purposes). Defaults to None.
        """
        if name is not None:
            self.name = name
        if category_id is not None:
            self.category_id = category_id

        Log.updated(self, actor)

    def get_dict(self) -> "IngredientDict":
        """Convert the Ingredient object to a dictionary suitable for API responses.

        Returns:
            IngredientDict: Dictionary with keys id, name, and category.
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
        }


class IngredientDict(TypedDict):
    """Type‑hinted dictionary representing an ingredient in API responses.

    Attributes:
        id: Unique identifier of the ingredient.
        name: Display name of the ingredient.
        category: Name of the ingredient's category.
    """

    id: int
    name: str
    category: str
