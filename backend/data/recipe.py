import enum
from datetime import datetime
from typing import Literal, TypedDict

from bafser import Image, Log, ObjMixin, SqlAlchemyBase, get_datetime_now
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from data import Tables, User
from data.recipe_category import RecipeCategory
from utils import normalize_for_search


class RecipeStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DELETED = "deleted"


type TRecipeStatus = Literal["draft", "published", "deleted"]


class Recipe(SqlAlchemyBase, ObjMixin):
    __tablename__ = Tables.Recipe
    __table_args__ = (
        Index("idx_recipe_status", "status"),
        Index("idx_recipe_category_id", "category_id"),
        Index("idx_recipe_author_id", "author_id"),
        Index("idx_recipe_title_normalized", "title_normalized"),
    )

    title: Mapped[str] = mapped_column(String(128))
    title_normalized: Mapped[str] = mapped_column(String(128), init=False)
    description: Mapped[str] = mapped_column(Text)
    active_time: Mapped[int]  # minutes
    total_time: Mapped[int]  # minutes
    difficulty: Mapped[int]  # 1-5
    author_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id", ondelete="RESTRICT"))
    category_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.RecipeCategory}.id", ondelete="RESTRICT"))
    main_image_id: Mapped[int | None] = mapped_column(ForeignKey(f"{Tables.Image}.id", ondelete="SET NULL"), default=None)

    rating: Mapped[float] = mapped_column(default=0.0)
    vote_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(init=False, default_factory=get_datetime_now)
    status: Mapped[RecipeStatus] = mapped_column(default="draft")
    published_at: Mapped[datetime | None] = mapped_column(default=None)

    author: Mapped[User] = relationship(foreign_keys=[author_id], lazy="joined", init=False)
    category: Mapped[RecipeCategory] = relationship(foreign_keys=[category_id], lazy="joined", init=False)
    main_image: Mapped[Image | None] = relationship(foreign_keys=[main_image_id], lazy="joined", init=False)

    @validates("title")
    def update_title_normalized(self, key: str, value: str):
        self.title_normalized = normalize_for_search(value)
        return value

    @staticmethod
    def new(
        title: str,
        description: str,
        active_time: int,
        total_time: int,
        difficulty: int,
        author: User,
        category_id: int,
        status: RecipeStatus = RecipeStatus.DRAFT,
        main_image_id: int | None = None,
        *,
        creator: User | None = None,
    ):
        obj = Recipe(
            title=title,
            description=description,
            active_time=active_time,
            total_time=total_time,
            difficulty=difficulty,
            author_id=author.id,
            category_id=category_id,
            status=status,
            main_image_id=main_image_id,
        )
        if status == RecipeStatus.PUBLISHED and obj.published_at is None:
            from bafser import get_datetime_now

            obj.published_at = get_datetime_now()
        Log.added(obj, creator)
        return obj

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        active_time: int | None = None,
        total_time: int | None = None,
        difficulty: int | None = None,
        category_id: int | None = None,
        main_image_id: int | None = None,
        status: RecipeStatus | None = None,
        *,
        actor: User | None = None,
    ):
        # Track status change for published_at
        old_status = self.status
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if active_time is not None:
            self.active_time = active_time
        if total_time is not None:
            self.total_time = total_time
        if difficulty is not None:
            self.difficulty = difficulty
        if category_id is not None:
            self.category_id = category_id
        if main_image_id is not None:
            if main_image_id != self.main_image_id:
                old_image = self.main_image
                if old_image:
                    old_image.delete2(actor=actor)
            self.main_image_id = main_image_id
        if status is not None:
            self.status = status
            # Update published_at based on status change
            if self.status == RecipeStatus.PUBLISHED and self.published_at is None:
                self.published_at = get_datetime_now()
            elif self.status in (RecipeStatus.DRAFT, RecipeStatus.DELETED) and old_status == RecipeStatus.PUBLISHED:
                self.published_at = None

        Log.updated(self, actor)

    def get_dict(self) -> "RecipeDict":
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author.login,
            "description": self.description,
            "active_time": self.active_time,
            "total_time": self.total_time,
            "difficulty": self.difficulty,
            "rating": self.rating,
            "vote_count": self.vote_count,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "category": self.category.name,
            "main_image": self.main_image.get_path() if self.main_image else None,
        }


class RecipeDict(TypedDict):
    id: int
    title: str
    author: str
    description: str
    active_time: int
    total_time: int
    difficulty: int
    rating: float
    vote_count: int
    created_at: str
    status: TRecipeStatus
    published_at: str | None
    category: str
    main_image: str | None
