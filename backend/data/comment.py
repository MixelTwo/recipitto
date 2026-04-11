from datetime import datetime
from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase, get_datetime_now
from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Comment(SqlAlchemyBase, ObjMixin):
    """Database model representing a user comment on a recipe.

    Attributes:
        user_id: ID of the user who wrote the comment.
        recipe_id: ID of the recipe being commented on.
        text: Comment text content.
        created_at: Timestamp when the comment was created.
        updated_at: Timestamp when the comment was last updated.
        user: Relationship to the User object.
        recipe: Relationship to the Recipe object.
    """

    __tablename__ = Tables.Comment
    __table_args__ = (
        Index("idx_comment_recipe_id", "recipe_id"),
        Index("idx_comment_user_id", "user_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id", ondelete="CASCADE"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(init=False, default_factory=get_datetime_now)
    updated_at: Mapped[datetime] = mapped_column(init=False, default_factory=get_datetime_now, onupdate=get_datetime_now)

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        text: str,
        *,
        creator: User | None = None,
        commit: bool = True,
    ) -> "Comment":
        """Create a new comment.

        Args:
            user_id: ID of the user who wrote the comment.
            recipe_id: ID of the recipe being commented on.
            text: Comment text content.
            creator: User who is creating the comment (for logging). Defaults to None.
            commit: Whether to commit the transaction immediately (default True).

        Returns:
            Comment: The newly created comment instance.
        """
        obj = Comment(
            user_id=user_id,
            recipe_id=recipe_id,
            text=text,
        )
        Log.added(obj, creator, commit=commit)
        return obj

    def update(
        self,
        text: str | None = None,
        *,
        actor: User | None = None,
    ):
        """Update the comment's fields.

        Args:
            text: New comment text (optional).
            actor: User who is performing the update (for logging). Defaults to None.
        """
        if text is not None:
            self.text = text
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["Comment"]:
        """Retrieve all comments for a specific recipe.

        Args:
            recipe_id: ID of the recipe.
            db_sess: Database session to use (optional).

        Returns:
            list[Comment]: List of comments, ordered by creation date descending.
        """
        return list(cls.query2(db_sess=db_sess).filter_by(recipe_id=recipe_id).order_by(cls.created_at.desc()).all())

    def get_dict(self) -> "CommentDict":
        """Convert the comment to a dictionary suitable for JSON serialization.

        Returns:
            CommentDict: Dictionary with id, user_id, recipe_id, text, and created_at.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }


class CommentDict(TypedDict):
    """Dictionary representation of a comment for API responses.

    Attributes:
        id: Comment ID.
        user_id: ID of the user who wrote the comment.
        recipe_id: ID of the recipe being commented on.
        text: Comment text content.
        created_at: ISO‑formatted timestamp of creation.
    """

    id: int
    user_id: int
    recipe_id: int
    text: str
    created_at: str
