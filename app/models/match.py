from __future__ import annotations

import uuid as uuid_pkg
from typing import TYPE_CHECKING, ClassVar, Self

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain import Score

from .base import Base

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
    score_json: Mapped[str | None] = mapped_column('Score')

    player1: Mapped[Player] = relationship('Player', foreign_keys=[player1_id])
    player2: Mapped[Player] = relationship('Player', foreign_keys=[player2_id])
    winner: Mapped[Player | None] = relationship('Player', foreign_keys=[winner_id])

    score: ClassVar[Score]

    @classmethod
    def start_new(cls, player1: Player, player2: Player) -> Self:
        ongoing_match = cls(uuid=uuid_pkg.uuid4(), player1=player1, player2=player2)
        ongoing_match.score = Score() # type: ignore[misc]
        return ongoing_match

    def get_view_match_model(self) -> dict[str, str | int]:
        view_score_model: dict[str, str | int] = self.score.get_view_score_model()
        return {
            'player1_name': self.player1.name,
            'player2_name': self.player2.name,
            **view_score_model,
        }

    def __repr__(self) -> str:
        return (
            f'<Match(id={self.id!r}, uuid={self.uuid!r}, '
            f'player1_id={self.player1_id!r}, player2_id={self.player2_id!r}, '
            f'winner_id={self.winner_id!r})>'
        )
