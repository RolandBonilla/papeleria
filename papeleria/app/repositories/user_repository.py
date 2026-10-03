from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(User)) or 0

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
