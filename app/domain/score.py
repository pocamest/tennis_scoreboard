from dataclasses import dataclass
from enum import IntEnum, StrEnum


class PlayerIdentifier(IntEnum):
    ONE = 0
    TWO = 1


class PointState(StrEnum):
    LOVE = '0'
    FIFTEEN = '15'
    THIRTY = '30'
    FORTY = '40'
    ADVANTAGE = 'AD'


@dataclass(frozen=True)
class Score:
    """
    Неизменяемый Объект-значение (Value Object), моделирующий счет матча.
    Его идентичность определяется совокупностью его атрибутов, а не ID.
    """

    _points: tuple[PointState, PointState] = (PointState.LOVE, PointState.LOVE)
    _games: tuple[int, int] = (0, 0)
    _sets: tuple[int, int] = (0, 0)

    def get_view_score_model(self) -> dict[str, str | int]:
        return {
            'player1_points': self._points[PlayerIdentifier.ONE],
            'player1_games': self._games[PlayerIdentifier.ONE],
            'player1_sets': self._sets[PlayerIdentifier.ONE],
            'player2_points': self._points[PlayerIdentifier.TWO],
            'player2_games': self._games[PlayerIdentifier.TWO],
            'player2_sets': self._sets[PlayerIdentifier.TWO],
        }
