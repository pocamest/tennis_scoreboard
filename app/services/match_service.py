import json
import math
import uuid as uuid_pkg
from typing import TypedDict

from app.database import Database
from app.domain import OngoingMatch, Player, PlayerIdentifier
from app.exceptions import InconsistentMatchStateError, MatchNotFoundError
from app.models import Match
from app.repositories import MatchRepository, PlayerRepository
from app.settings import settings
from app.store import OngoingMatchStore


class FinishedMatchDict(TypedDict):
    player1_name: str
    player2_name: str
    winner_name: str


class PaginatedMatchesDict(TypedDict):
    matches: list[FinishedMatchDict]
    total_pages: int
    current_page: int


class MatchService:
    def __init__(self, db: Database, ongoing_match_store: OngoingMatchStore):
        self._db = db
        self._ongoing_match_store = ongoing_match_store

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

        if new_ongoing_match.is_finished:
            winner = new_ongoing_match.winner
            if winner is None:
                raise InconsistentMatchStateError(
                    'The match is over but the winner has not been determined'
                )
            with self._db.get_session() as session:
                match_ = Match(
                    uuid=new_ongoing_match.uuid,
                    player1_id=new_ongoing_match.player1.id,
                    player2_id=new_ongoing_match.player2.id,
                    winner_id=winner.id,
                    score_json=json.dumps(
                        new_ongoing_match.score.get_final_score_data()
                    ),
                )

                match_repo = MatchRepository(session)
                match_repo.add(match_)

            self._ongoing_match_store.delete(new_ongoing_match.uuid)
        else:
            self._ongoing_match_store.put(new_ongoing_match)
        return new_ongoing_match

    def get_finished_matches_paginated(
        self, page: int, player_name: str | None
    ) -> PaginatedMatchesDict:
        limit = settings.default_page_size
        offset = (page - 1) * limit

        with self._db.get_session() as session:
            player_repo = PlayerRepository(session)
            match_repo = MatchRepository(session)

            player_orm = None

            if player_name:
                player_orm = player_repo.find_one_by_name(player_name)

                if player_orm is None:
                    return {'matches': [], 'total_pages': 0, 'current_page': page}

            matches_orm, total_matches = match_repo.find_many(
                limit=limit,
                offset=offset,
                player=player_orm,
            )

            matches_dto: list[FinishedMatchDict] = [
                {
                    'player1_name': m.player1.name,
                    'player2_name': m.player2.name,
                    'winner_name': m.winner.name,
                }
                for m in matches_orm
            ]

            total_pages = math.ceil(total_matches / limit) if total_matches > 0 else 0

            return {
                'matches': matches_dto,
                'total_pages': total_pages,
                'current_page': page,
            }
