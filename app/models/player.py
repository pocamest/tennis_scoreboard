from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from .match import Match


class Player(Base):
    __tablename__ = 'Players'

    id: Mapped[int] = mapped_column('ID', primary_key=True)
    name: Mapped[str] = mapped_column('Name', String(255), unique=True, nullable=False)

    matches: Mapped[list[Match]] = relationship(
        'Match',
        primaryjoin='or_(Player.id == Match.player1_id, Player.id == Match.player2_id)',
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f'<Player(id={self.id!r}, name={self.name!r})>'
