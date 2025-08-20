from __future__ import annotations

import uuid as uuid_pkg
from typing import TYPE_CHECKING

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from .player import Player


class Match(Base):
    __tablename__ = 'Matches'

    id: Mapped[int] = mapped_column('ID', primary_key=True)
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        'UUID', SQLAlchemyUUID(as_uuid=True), nullable=False, unique=True
    )
    player1_id: Mapped[int] = mapped_column(
        'Player1', ForeignKey('Players.ID'), nullable=False
    )
    player2_id: Mapped[int] = mapped_column(
        'Player2', ForeignKey('Players.ID'), nullable=False
    )
    winner_id: Mapped[int | None] = mapped_column(
        'Winner',
        ForeignKey('Players.ID'),
    )
    score: Mapped[str | None] = mapped_column('Score')

    player1: Mapped[Player] = relationship('Player', foreign_keys=[player1_id])
    player2: Mapped[Player] = relationship('Player', foreign_keys=[player2_id])
    winner: Mapped[Player | None] = relationship('Player', foreign_keys=[winner_id])

    def __repr__(self) -> str:
        return (
            f'<Match(id={self.id!r}, uuid={self.uuid!r}, '
            f'player1_id={self.player1_id!r}, player2_id={self.player2_id!r}, '
            f'winner_id={self.winner_id!r})>'
        )
