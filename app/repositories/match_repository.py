from sqlalchemy.orm import Session, joinedload

from app.models import Match


class MatchRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all_matches(self) -> list[Match]:
        return (
            self._session.query(Match)
            .options(joinedload(Match.player1), joinedload(Match.player2))
            .all()
        )
