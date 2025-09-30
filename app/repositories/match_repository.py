from sqlalchemy.orm import Session

from app.models import Match


class MatchRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, match_: Match) -> None:
        self._session.add(match_)
