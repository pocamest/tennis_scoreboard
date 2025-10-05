from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Match, Player


class MatchRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, match_: Match) -> None:
        self._session.add(match_)

    def find_many(
        self, *, limit: int, offset: int, player: Player | None = None
    ) -> tuple[Sequence[Match], int]:
        stmt = select(Match).options(
            joinedload(Match.player1, innerjoin=True),
            joinedload(Match.player2, innerjoin=True),
            joinedload(Match.winner, innerjoin=True),
        )

        if player:
            stmt = stmt.where(
                or_(
                    Match.player1_id == player.id,
                    Match.player2_id == player.id,
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_matches = self._session.execute(count_stmt).scalar() or 0

        stmt = stmt.order_by(Match.id.desc()).limit(limit).offset(offset)

        matches = self._session.scalars(stmt).all()
        return matches, total_matches
