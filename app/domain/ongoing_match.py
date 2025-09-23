import uuid as uuid_pkg
from dataclasses import dataclass, field, replace
from typing import ClassVar, Self

from .player import Player
from .score import PlayerIdentifier, Score


@dataclass(frozen=True)
class OngoingMatch:
    _SETS_TO_WIN_MATCH: ClassVar[int] = 2

    player1: Player
    player2: Player

    uuid: uuid_pkg.UUID = field(default_factory=uuid_pkg.uuid4, init=False)
    score: Score = field(default_factory=Score, init=False)

    def get_view_match_model(self) -> dict[str, str | int]:
        view_score_model: dict[str, str | int] = self.score.get_view_score_model()
        return {
            'player1_name': self.player1.name,
            'player2_name': self.player2.name,
            **view_score_model,
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
