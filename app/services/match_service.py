import uuid as uuid_pkg

from app.database import Database
from app.domain import OngoingMatch, Player, PlayerIdentifier
from app.exceptions import MatchNotFoundError
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

    def create_new_match(self, player1_name: str, player2_name: str) -> OngoingMatch:
        with self._db.get_session() as session:
            player_repo = PlayerRepository(session)

            p1_orm = player_repo.find_or_create(player1_name)
            p2_orm = player_repo.find_or_create(player2_name)

            session.flush()

            p1_domain = Player(id=p1_orm.id, name=p1_orm.name)
            p2_domain = Player(id=p2_orm.id, name=p2_orm.name)

        ongoing_match = OngoingMatch(player1=p1_domain, player2=p2_domain)
        self._ongoing_match_store.put(ongoing_match)
        return ongoing_match

    def get_ongoing_match(self, uuid: uuid_pkg.UUID) -> OngoingMatch:
        ongoing_match = self._ongoing_match_store.find_one(uuid)
        if ongoing_match is None:
            raise MatchNotFoundError(f'Ongoing match with UUID {uuid} not found')
        return ongoing_match

    def record_point(
        self, uuid: uuid_pkg.UUID, point_winner: PlayerIdentifier
    ) -> OngoingMatch:
        ongoing_match = self._ongoing_match_store.find_one(uuid)
        if ongoing_match is None:
            raise MatchNotFoundError(f'Ongoing match with UUID {uuid} not found')

        new_ongoing_match = ongoing_match.add_point(point_winner)
        self._ongoing_match_store.put(new_ongoing_match)
        return new_ongoing_match
