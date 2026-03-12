from datetime import datetime
from typing import TypedDict

from bafser import Log, SqlAlchemyBase, get_datetime_now, get_db_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Favorite(SqlAlchemyBase):
    __tablename__ = Tables.Favorite

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(init=False, default=get_datetime_now)

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        *,
        creator: User | None = None,
    ):
        obj = Favorite(
            user_id=user_id,
            recipe_id=recipe_id,
        )
        Log.added(obj, creator)
        return obj

    @classmethod
    def get_by_user(cls, user_id: int, *, db_sess: Session | None = None) -> list["Favorite"]:
        db_sess = db_sess or get_db_session()
        return list(db_sess.query(cls).filter_by(user_id=user_id).order_by(cls.added_at.desc()).all())

    @classmethod
    def get_by_user_and_recipe(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> "Favorite | None":
        db_sess = db_sess or get_db_session()
        return db_sess.query(cls).filter_by(user_id=user_id, recipe_id=recipe_id).first()

    @classmethod
    def exists(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> bool:
        return cls.get_by_user_and_recipe(user_id, recipe_id, db_sess=db_sess) is not None

    def get_dict(self) -> "FavoriteDict":
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "added_at": self.added_at.isoformat(),
        }


class FavoriteDict(TypedDict):
    user_id: int
    recipe_id: int
    added_at: str
