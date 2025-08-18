from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Player(Base):
    __tablename__ = 'Players'

    id: Mapped[int] = mapped_column('ID', primary_key=True)
    name: Mapped[str] = mapped_column('Name', String(255), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Player(id={self.id!r}, name={self.name!r})>'
