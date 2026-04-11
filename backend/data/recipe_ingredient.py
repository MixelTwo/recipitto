from typing import TypedDict

from bafser import Log, SqlAlchemyBase, get_db_session
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.ingredient import Ingredient
from data.recipe import Recipe


class RecipeIngredient(SqlAlchemyBase):
    """Database model representing an ingredient used in a recipe.

    Attributes:
        recipe_id: ID of the recipe that uses this ingredient.
        ingredient_id: ID of the ingredient being used.
        quantity: Amount of the ingredient needed (e.g., 2.5).
        unit: Measurement unit (e.g., "cups", "grams", "tablespoons").
        recipe: Relationship to the Recipe object.
        ingredient: Relationship to the Ingredient object (joined by default).
    """

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
        commit: bool = True,
    ) -> "RecipeIngredient":
        """Create a new RecipeIngredient record.

        Args:
            recipe_id: ID of the recipe that will use the ingredient.
            ingredient_id: ID of the ingredient to associate.
            quantity: Amount of the ingredient needed.
            unit: Measurement unit for the quantity.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.
            commit: Whether to commit the transaction immediately (default True).

        Returns:
            RecipeIngredient: The newly created RecipeIngredient object.
        """
        obj = RecipeIngredient(
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
        )
        Log.added(obj, creator, commit=commit)
        return obj

    def update(
        self,
        quantity: float | None = None,
        unit: str | None = None,
        *,
        actor: User | None = None,
    ):
        """Update the ingredient's quantity and/or unit.

        Args:
            quantity: New quantity value, or None to keep the current value.
            unit: New unit string, or None to keep the current value.
            actor: Optional User object representing who performed the update
                (for logging purposes). Defaults to None.
        """
        if quantity is not None:
            self.quantity = quantity
        if unit is not None:
            self.unit = unit
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["RecipeIngredient"]:
        """Retrieve all ingredients associated with a given recipe.

        Args:
            recipe_id: ID of the recipe whose ingredients to retrieve.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            list[RecipeIngredient]: List of RecipeIngredient objects for the recipe.
        """
        db_sess = db_sess or get_db_session()
        return list(db_sess.query(cls).filter_by(recipe_id=recipe_id).all())

    @classmethod
    def get_by_recipe_and_ingredient(cls, recipe_id: int, ingredient_id: int, *, db_sess: Session | None = None) -> "RecipeIngredient | None":
        """Retrieve a specific RecipeIngredient by recipe and ingredient IDs.

        Args:
            recipe_id: ID of the recipe.
            ingredient_id: ID of the ingredient.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            RecipeIngredient | None: The RecipeIngredient object if found, otherwise None.
        """
        db_sess = db_sess or get_db_session()
        return db_sess.query(cls).filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first()

    @classmethod
    def exists(cls, recipe_id: int, ingredient_id: int, *, db_sess: Session | None = None) -> bool:
        """Check whether a RecipeIngredient exists for the given recipe and ingredient.

        Args:
            recipe_id: ID of the recipe.
            ingredient_id: ID of the ingredient.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            bool: True if the RecipeIngredient exists, False otherwise.
        """
        return cls.get_by_recipe_and_ingredient(recipe_id, ingredient_id, db_sess=db_sess) is not None

    def get_dict(self) -> "RecipeIngredientDict":
        """Convert the RecipeIngredient object to a dictionary suitable for API responses.

        Returns:
            RecipeIngredientDict: Dictionary with keys recipe_id, ingredient_id,
                quantity, unit, and ingredient_name.
        """
        return {
            "recipe_id": self.recipe_id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "ingredient_name": self.ingredient.name,
        }


class RecipeIngredientDict(TypedDict):
    """Type‑hinted dictionary representing a recipe ingredient in API responses.

    Attributes:
        recipe_id: ID of the recipe that uses this ingredient.
        ingredient_id: ID of the ingredient being used.
        quantity: Amount of the ingredient needed.
        unit: Measurement unit for the quantity.
        ingredient_name: Display name of the ingredient.
    """

    recipe_id: int
    ingredient_id: int
    quantity: float
    unit: str
    ingredient_name: str
