from typing import TypedDict

from bafser import Image, Log, ObjMixin, SqlAlchemyBase
from flask import url_for
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class RecipeImage(SqlAlchemyBase, ObjMixin):
    """Database model representing an image associated with a recipe.

    Attributes:
        recipe_id: ID of the recipe that owns this image.
        image_id: ID of the Image record containing the actual image data.
        recipe: Relationship to the Recipe object.
        image: Relationship to the Image object (joined by default).
    """

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
        commit: bool = True,
    ) -> "RecipeImage":
        """Create a new RecipeImage record.

        Args:
            recipe_id: ID of the recipe that will own the image.
            image_id: ID of the Image record to associate.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.
            commit: Whether to commit the transaction immediately (default True).

        Returns:
            RecipeImage: The newly created RecipeImage object.
        """
        obj = RecipeImage(
            recipe_id=recipe_id,
            image_id=image_id,
        )
        Log.added(obj, creator, commit=commit)
        return obj

    @classmethod
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["RecipeImage"]:
        """Retrieve all images associated with a given recipe.

        Args:
            recipe_id: ID of the recipe whose images to retrieve.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            list[RecipeImage]: List of RecipeImage objects for the recipe.
        """
        return list(cls.query2(db_sess=db_sess).filter_by(recipe_id=recipe_id).all())

    @classmethod
    def get_by_recipe_and_image(cls, recipe_id: int, image_id: int, *, db_sess: Session | None = None) -> "RecipeImage | None":
        """Retrieve a specific RecipeImage by recipe and image IDs.

        Args:
            recipe_id: ID of the recipe.
            image_id: ID of the image.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            RecipeImage | None: The RecipeImage object if found, otherwise None.
        """
        return cls.query2(db_sess=db_sess).filter_by(recipe_id=recipe_id, image_id=image_id).first()

    def get_dict(self) -> "RecipeImageDict":
        """Convert the RecipeImage object to a dictionary suitable for API responses.

        Returns:
            RecipeImageDict: Dictionary with keys id, recipe_id, image_id, and image_path.
        """
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "image_id": self.image_id,
            "image_path": url_for("images.img", imgId=self.image_id),
        }


class RecipeImageDict(TypedDict):
    """Type‑hinted dictionary representing a recipe image in API responses.

    Attributes:
        id: Unique identifier of the RecipeImage record.
        recipe_id: ID of the recipe that owns the image.
        image_id: ID of the Image record.
        image_path: Filesystem path or URL to the image file.
    """

    id: int
    recipe_id: int
    image_id: int
    image_path: str
