import uuid as uuid_pkg
from dataclasses import dataclass, field

from .player import Player
from .score import Score


@dataclass
class OngoingMatch:
    player1: Player
    player2: Player
    uuid: uuid_pkg.UUID = field(init=False)
    score: Score = field(init=False)

    def __post_init__(self) -> None:
        self.uuid = uuid_pkg.uuid4()
        self.score =Score()

    def get_view_match_model(self) -> dict[str, str | int]:
        view_score_model: dict[str, str | int] = self.score.get_view_score_model()
        return {
            'player1_name': self.player1.name,
            'player2_name': self.player2.name,
            **view_score_model,
        }
