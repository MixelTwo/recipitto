from datetime import datetime
from typing import TypedDict

from bafser import Log, ObjMixin, SqlAlchemyBase, get_datetime_now
from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Comment(SqlAlchemyBase, ObjMixin):
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
    def get_by_recipe(cls, recipe_id: int, *, db_sess: Session | None = None) -> list["Comment"]:
        return list(cls.query2(db_sess=db_sess).filter_by(recipe_id=recipe_id).order_by(cls.created_at.desc()).all())

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
