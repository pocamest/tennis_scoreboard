from app.database import Database
from app.models import Match
from app.repositories import MatchRepository


class MatchService:
    def __init__(self, db: Database):
        self._db = db

    def get_all_matches(self) -> list[Match]:
        with self._db.get_session() as session:
            match_repo = MatchRepository(session)
            return match_repo.find_all_matches_with_players()
