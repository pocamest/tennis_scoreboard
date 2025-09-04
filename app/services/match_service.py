import uuid as uuid_pkg

from app.database import Database
from app.models import Match
from app.repositories import MatchRepository, PlayerRepository
from app.store import OngoingMatchStore


class MatchService:
    def __init__(self, db: Database, ongoing_match_store: OngoingMatchStore):
        self._db = db
        self._ongoing_match_store = ongoing_match_store

    def get_all_matches(self) -> list[Match]:
        with self._db.get_session() as session:
            match_repo = MatchRepository(session)
            return match_repo.find_all_matches_with_players()

    def create_new_match(self, player1_name: str, player2_name: str) -> Match:
        with self._db.get_session() as session:
            player_repo = PlayerRepository(session)

            player1 = player_repo.find_or_create(player1_name)
            player2 = player_repo.find_or_create(player2_name)

            session.flush()

            ongoing_match = Match(
                uuid=uuid_pkg.uuid4(), player1=player1, player2=player2
            )
        self._ongoing_match_store.put(ongoing_match)
        return ongoing_match
