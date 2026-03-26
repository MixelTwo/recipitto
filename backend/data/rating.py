from typing import TypedDict

from bafser import Log, SqlAlchemyBase, get_db_session
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data import Tables, User
from data.recipe import Recipe


class Rating(SqlAlchemyBase):
    __tablename__ = Tables.Rating

    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Recipe}.id", ondelete="CASCADE"), primary_key=True)
    rating: Mapped[int]  # 1-5

    user: Mapped[User] = relationship(foreign_keys=[user_id], init=False)
    recipe: Mapped[Recipe] = relationship(foreign_keys=[recipe_id], init=False)

    @staticmethod
    def new(
        user_id: int,
        recipe_id: int,
        rating: int,
        *,
        creator: User | None = None,
    ):
        obj = Rating(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=rating,
        )
        Log.added(obj, creator)
        return obj

    def update(
        self,
        rating: int | None = None,
        *,
        actor: User | None = None,
    ):
        if rating is not None:
            self.rating = rating
        Log.updated(self, actor)

    @classmethod
    def get_stats(cls, recipe_id: int, *, db_sess: Session | None = None) -> tuple[float, int, dict[str, int]]:
        """Return (average, count, distribution) for a recipe."""
        db_sess = db_sess or get_db_session()
        avg_result = db_sess.query(func.avg(cls.rating)).filter_by(recipe_id=recipe_id).scalar()
        count_result = db_sess.query(func.count(cls.rating)).filter_by(recipe_id=recipe_id).scalar()
        avg = float(avg_result) if avg_result else 0.0
        count = count_result if count_result else 0
        distribution: dict[str, int] = {}
        for i in range(1, 6):
            dist_count = db_sess.query(func.count(cls.rating)).filter_by(recipe_id=recipe_id, rating=i).scalar()
            distribution[str(i)] = dist_count
        return avg, count, distribution

    @classmethod
    def recalculate_recipe_stats(cls, recipe_id: int, *, db_sess: Session | None = None) -> None:
        """Update Recipe.rating and Recipe.vote_count based on current ratings."""
        recipe = Recipe.get2(recipe_id, db_sess=db_sess)
        if not recipe:
            return
        avg, count, _ = cls.get_stats(recipe_id, db_sess=db_sess)
        recipe.rating = avg
        recipe.vote_count = count
        recipe.db_sess.commit()

    @classmethod
    def get_by_user_and_recipe(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> "Rating | None":
        db_sess = db_sess or get_db_session()
        return db_sess.query(cls).filter_by(user_id=user_id, recipe_id=recipe_id).first()

    @classmethod
    def exists(cls, user_id: int, recipe_id: int, *, db_sess: Session | None = None) -> bool:
        return cls.get_by_user_and_recipe(user_id, recipe_id, db_sess=db_sess) is not None

    def get_dict(self) -> "RatingDict":
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id,
            "rating": self.rating,
        }


class RatingDict(TypedDict):
    user_id: int
    recipe_id: int
    rating: int
