from typing import TypedDict

from bafser import Image, Log, ObjMixin, SqlAlchemyBase, get_db_session
from flask import url_for
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class RecipeStep(SqlAlchemyBase, ObjMixin):
    """Database model representing a step in a recipe.

    Attributes:
        recipe_id: ID of the recipe that contains this step.
        step_number: Sequential number of the step (1‑based).
        text: Description of the step.
        image_id: Optional ID of an Image associated with the step.
        recipe: Relationship to the Recipe object.
        image: Relationship to the Image object (joined by default), or None.
    """

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
        commit: bool = True,
    ) -> "RecipeStep":
        """Create a new RecipeStep record.

        Args:
            recipe_id: ID of the recipe that will contain the step.
            step_number: Sequential number of the step.
            text: Description of the step.
            image_id: Optional ID of an Image to associate with the step.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.
            commit: Whether to commit the transaction immediately (default True).

        Returns:
            RecipeStep: The newly created RecipeStep object.
        """
        obj = RecipeStep(
            recipe_id=recipe_id,
            step_number=step_number,
            text=text,
            image_id=image_id,
        )
        Log.added(obj, creator, commit=commit)
        return obj

    def update(
        self,
        step_number: int | None = None,
        text: str | None = None,
        image_id: int | None = None,
        *,
        actor: User | None = None,
    ):
        """Update the step's fields.

        Args:
            step_number: New step number, or None to keep the current value.
            text: New step description, or None to keep the current value.
            image_id: New image ID, or None to keep the current value.
                If changed and the old image exists, the old image will be deleted.
            actor: Optional User object representing who performed the update
                (for logging purposes). Defaults to None.
        """
        if step_number is not None:
            self.step_number = step_number
        if text is not None:
            self.text = text
        if image_id is not None:
            if image_id != self.image_id:
                old_image = self.image
                if old_image:
                    old_image.delete2(actor=actor)
            self.image_id = image_id
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["RecipeStep"]:
        """Retrieve all steps associated with a given recipe.

        Args:
            recipe_id: ID of the recipe whose steps to retrieve.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            list[RecipeStep]: List of RecipeStep objects for the recipe.
        """
        db_sess = db_sess or get_db_session()
        return list(db_sess.query(cls).filter_by(recipe_id=recipe_id).all())

    def get_dict(self) -> "RecipeStepDict":
        """Convert the RecipeStep object to a dictionary suitable for API responses.

        Returns:
            RecipeStepDict: Dictionary with keys id, recipe_id, step_number,
                text, and image (path string or None).
        """
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "step_number": self.step_number,
            "text": self.text,
            "image": url_for("images.img", imgId=self.image_id) if self.image_id else None,
        }


class RecipeStepDict(TypedDict):
    """Type‑hinted dictionary representing a recipe step in API responses.

    Attributes:
        id: Unique identifier of the RecipeStep record.
        recipe_id: ID of the recipe that contains the step.
        step_number: Sequential number of the step.
        text: Description of the step.
        image: Filesystem path or URL to the step's image, or None if no image.
    """

    id: int
    recipe_id: int
    step_number: int
    text: str
    image: str | None
