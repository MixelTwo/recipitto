from datetime import datetime
from typing import TypedDict

from bafser import Log, SqlAlchemyBase, get_datetime_now, get_db_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Favorite(SqlAlchemyBase):
    """Database model representing a user's favorite recipe.

    Attributes:
        user_id: ID of the user who favorited the recipe.
        recipe_id: ID of the recipe that was favorited.
        added_at: Timestamp when the favorite was added.
        user: Relationship to the User object.
        recipe: Relationship to the Recipe object.
    """

    __tablename__ = Tables.Favorite

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(init=False, default_factory=get_datetime_now)

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        *,
        creator: User | None = None,
        commit: bool = True,
    ) -> "Favorite":
        """Create a new Favorite record.

        Args:
            user_id: ID of the user who is favoriting the recipe.
            recipe_id: ID of the recipe being favorited.
            creator: Optional User object representing who created this record
                (for logging purposes). Defaults to None.
            commit: Whether to commit the transaction immediately (default True).

        Returns:
            Favorite: The newly created Favorite object.
        """
        obj = Favorite(
            user_id=user_id,
            recipe_id=recipe_id,
        )
        Log.added(obj, creator, commit=commit)
        return obj

    @classmethod
    def get_by_user(cls, user_id: int, *, db_sess: Session | None = None) -> list["Favorite"]:
        """Retrieve all favorites for a given user.

        Args:
            user_id: ID of the user whose favorites to retrieve.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            list[Favorite]: List of Favorite objects, ordered by added_at descending.
        """
        db_sess = db_sess or get_db_session()
        return list(db_sess.query(cls).filter_by(user_id=user_id).order_by(cls.added_at.desc()).all())

    @classmethod
    def get_by_user_and_recipe(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> "Favorite | None":
        """Retrieve a specific favorite by user and recipe.

        Args:
            user_id: ID of the user.
            recipe_id: ID of the recipe.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            Favorite | None: The Favorite object if found, otherwise None.
        """
        db_sess = db_sess or get_db_session()
        return db_sess.query(cls).filter_by(user_id=user_id, recipe_id=recipe_id).first()

    @classmethod
    def exists(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> bool:
        """Check whether a favorite exists for the given user and recipe.

        Args:
            user_id: ID of the user.
            recipe_id: ID of the recipe.
            db_sess: Optional database session. If not provided, a new session
                will be acquired.

        Returns:
            bool: True if the favorite exists, False otherwise.
        """
        return cls.get_by_user_and_recipe(user_id, recipe_id, db_sess=db_sess) is not None

    def get_dict(self) -> "FavoriteDict":
        """Convert the Favorite object to a dictionary suitable for API responses.

        Returns:
            FavoriteDict: Dictionary with keys user_id, recipe_id, and added_at.
        """
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "added_at": self.added_at.isoformat(),
        }


class FavoriteDict(TypedDict):
    """Type‑hinted dictionary representing a favorite in API responses.

    Attributes:
        user_id: ID of the user who favorited the recipe.
        recipe_id: ID of the recipe that was favorited.
        added_at: ISO‑formatted timestamp when the favorite was added.
    """

    user_id: int
    recipe_id: int
    added_at: str
