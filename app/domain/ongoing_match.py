import uuid as uuid_pkg
from dataclasses import dataclass, field, replace
from typing import ClassVar, Self, TypedDict

from .player import Player
from .score import PlayerIdentifier, Score


class MatchViewDict(TypedDict):
    uuid: str
    is_finished: bool
    winner_name: str | None

    player1_name: str
    player1_sets: int
    player1_games: int
    player1_points: str | int

    player2_name: str
    player2_sets: int
    player2_games: int
    player2_points: str | int


@dataclass(frozen=True)
class OngoingMatch:
    _SETS_TO_WIN_MATCH: ClassVar[int] = 2

    player1: Player
    player2: Player

    uuid: uuid_pkg.UUID = field(default_factory=uuid_pkg.uuid4)
    score: Score = field(default_factory=Score)

    def get_view_model(self) -> MatchViewDict:
        view_score = (
            self.score.as_final_view_score()
            if self.is_finished
            else self.score.as_current_view_score()
        )
        winner_name = self.winner.name if self.winner is not None else None
        return {
            'uuid': str(self.uuid),
            'is_finished': self.is_finished,
            'winner_name': winner_name,
            'player1_name': self.player1.name,
            'player1_sets': view_score.player1_sets,
            'player1_games': view_score.player1_games,
            'player1_points': view_score.player1_points,
            'player2_name': self.player2.name,
            'player2_sets': view_score.player2_sets,
            'player2_games': view_score.player2_games,
            'player2_points': view_score.player2_points,
        }

    def add_point(self, point_winner: PlayerIdentifier) -> Self:
        new_score = self.score.add_point(point_winner)
        return replace(self, score=new_score)

    @property
    def is_finished(self) -> bool:
        return max(self.score.sets) == self._SETS_TO_WIN_MATCH

    @property
    def winner(self) -> Player | None:
        if not self.is_finished:
            return None

        p1_sets, p2_sets = self.score.sets
        return self.player1 if p1_sets > p2_sets else self.player2
