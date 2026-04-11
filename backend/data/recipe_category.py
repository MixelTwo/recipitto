from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from data import Tables, User
from utils import normalize_for_search


class RecipeCategory(SqlAlchemyBase, ObjMixin):
    """Database model representing a category for recipes.

    Attributes:
        name: Display name of the category (max 64 characters).
        name_normalized: Normalized version of the name for search purposes.
    """

    __tablename__ = Tables.RecipeCategory
    name: Mapped[str] = mapped_column(String(64))
    name_normalized: Mapped[str] = mapped_column(String(64), init=False)

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
    def new(name: str, *, creator: User | None = None) -> "RecipeCategory":
        """Create a new RecipeCategory record.

        Args:
            name: Display name for the category.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.

        Returns:
            RecipeCategory: The newly created RecipeCategory object.
        """
        obj = RecipeCategory(name=name)
        Log.added(obj, creator)
        return obj

    def update(self, name: str | None, *, actor: User | None = None):
        """Update the category's fields.

        Args:
            name: New name for the category, or None to keep the current value.
            actor: Optional User object representing who performed the update
                (for logging purposes). Defaults to None.
        """
        if name is not None:
            self.name = name
        Log.updated(self, actor)

    def get_dict(self) -> "RecipeCategoryDict":
        """Convert the RecipeCategory object to a dictionary suitable for API responses.

        Returns:
            RecipeCategoryDict: Dictionary with keys id and name.
        """
        return {
            "id": self.id,
            "name": self.name,
        }


class RecipeCategoryDict(TypedDict):
    """Type‑hinted dictionary representing a recipe category in API responses.

    Attributes:
        id: Unique identifier of the category.
        name: Display name of the category.
    """

    id: int
    name: str
