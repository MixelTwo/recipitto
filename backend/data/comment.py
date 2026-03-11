from datetime import datetime
from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase, get_datetime_now
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from data import Tables, User
from data.recipe import Recipe


class Comment(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.Comment

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(init=False, default=get_datetime_now)

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        text: str,
        *,
        creator: User | None = None,
    ):
        obj = Comment(
            user_id=user_id,
            recipe_id=recipe_id,
            text=text,
        )
        Log.added(obj, creator)
        return obj

    def update(
        self,
        text: str | None = None,
        *,
        actor: User | None = None,
    ):
        if text is not None:
            self.text = text
        Log.updated(self, actor)

    @classmethod
    def get_by_recipe(cls, db_sess: Session, recipe_id: int) -> list["Comment"]:
        return list(db_sess.query(cls).filter_by(recipe_id=recipe_id).order_by(cls.created_at.desc()).all())

    def get_dict(self) -> "CommentDict":
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }


class CommentDict(TypedDict):
    id: int
    user_id: int
    recipe_id: int
    text: str
    created_at: str
