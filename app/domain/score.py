from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum, StrEnum
from typing import ClassVar, Self, TypeVar


class PlayerIdentifier(IntEnum):
    ONE = 0
    TWO = 1

    @property
    def opponent(self) -> PlayerIdentifier:
        if self is PlayerIdentifier.ONE:
            return PlayerIdentifier.TWO
        return PlayerIdentifier.ONE


class PointState(StrEnum):
    LOVE = '0'
    FIFTEEN = '15'
    THIRTY = '30'
    FORTY = '40'
    ADVANTAGE = 'AD'


# "Компонент Счета" - это атомарная часть счета, т.е. очки, геймы или сеты.
# Технически, это может быть либо PointState (для очков), либо int (для геймов/сетов).
TScoreComponent = TypeVar('TScoreComponent', PointState, int)


@dataclass(frozen=True)
class Score:
    """
    Неизменяемый Объект-значение (Value Object), моделирующий счет матча.
    Его идентичность определяется совокупностью его атрибутов, а не ID.
    """

    points: tuple[PointState, PointState] = (PointState.LOVE, PointState.LOVE)
    games: tuple[int, int] = (0, 0)
    sets: tuple[int, int] = (0, 0)

    _NORMAL_POINT_TRANSITION: ClassVar[dict[PointState, PointState]] = {
        PointState.LOVE: PointState.FIFTEEN,
        PointState.FIFTEEN: PointState.THIRTY,
        PointState.THIRTY: PointState.FORTY,
    }

    _GAMES_TO_WIN_SET: ClassVar[int] = 6
    _GAMES_FOR_TIE_BREAK: ClassVar[tuple[int, int]] = (6, 6)
    _MIN_GAME_DIFFERENCE_FOR_SET_WIN: ClassVar[int] = 2

    def get_view_score_model(self) -> dict[str, str | int]:
        return {
            'player1_points': self.points[PlayerIdentifier.ONE],
            'player1_games': self.games[PlayerIdentifier.ONE],
            'player1_sets': self.sets[PlayerIdentifier.ONE],
            'player2_points': self.points[PlayerIdentifier.TWO],
            'player2_games': self.games[PlayerIdentifier.TWO],
            'player2_sets': self.sets[PlayerIdentifier.TWO],
        }

    def add_point(self, winner: PlayerIdentifier) -> Self:
        if PointState.ADVANTAGE in self.points or (
            self.points == (PointState.FORTY, PointState.FORTY)
        ):
            return self._handle_deuce_advantage_point(winner)
        elif PointState.FORTY in self.points:
            return self._handle_game_point(winner)
        else:
            return self._handle_normal_point(winner)

    def _build_score_component_tuple(
        self,
        winner: PlayerIdentifier,
        winner_score_component: TScoreComponent,
        opponent_score_component: TScoreComponent,
    ) -> tuple[TScoreComponent, TScoreComponent]:
        if winner is PlayerIdentifier.ONE:
            return winner_score_component, opponent_score_component
        return opponent_score_component, winner_score_component

    def _handle_normal_point(self, winner: PlayerIdentifier) -> Self:
        opponent = winner.opponent
        opponent_points = self.points[opponent]

        winner_points = self._NORMAL_POINT_TRANSITION[self.points[winner]]

        new_points = self._build_score_component_tuple(
            winner=winner,
            winner_score_component=winner_points,
            opponent_score_component=opponent_points,
        )
        return replace(self, points=new_points)

    def _handle_game_point(self, winner: PlayerIdentifier) -> Self:
        if self.points[winner] is PointState.FORTY:
            return self._win_game(winner)
        return self._handle_normal_point(winner)

    def _handle_deuce_advantage_point(self, winner: PlayerIdentifier) -> Self:
        if self.points == (PointState.FORTY, PointState.FORTY):
            opponent = winner.opponent
            opponent_points = self.points[opponent]
            winner_points = PointState.ADVANTAGE
            new_points = self._build_score_component_tuple(
                winner=winner,
                winner_score_component=winner_points,
                opponent_score_component=opponent_points,
            )
            return replace(self, points=new_points)

        if self.points[winner] is PointState.ADVANTAGE:
            return self._win_game(winner)

        return replace(self, points=(PointState.FORTY, PointState.FORTY))

    def _win_game(self, winner: PlayerIdentifier) -> Self:
        opponent = winner.opponent
        opponent_games = self.games[opponent]
        winner_games = self.games[winner] + 1
        new_games = self._build_score_component_tuple(
            winner=winner,
            winner_score_component=winner_games,
            opponent_score_component=opponent_games,
        )

        if (
            winner_games >= self._GAMES_TO_WIN_SET
            and winner_games - opponent_games >= self._MIN_GAME_DIFFERENCE_FOR_SET_WIN
        ):
            return self._win_set(winner)

        if new_games == self._GAMES_FOR_TIE_BREAK:
            return self._tie_break(winner)

        return replace(self, points=(PointState.LOVE, PointState.LOVE), games=new_games)

    def _win_set(self, winner: PlayerIdentifier) -> Self:
        opponent = winner.opponent
        opponent_sets = self.sets[opponent]
        winner_sets = self.sets[winner] + 1
        new_sets = self._build_score_component_tuple(
            winner=winner,
            winner_score_component=winner_sets,
            opponent_score_component=opponent_sets,
        )
        return replace(
            self, points=(PointState.LOVE, PointState.LOVE), games=(0, 0), sets=new_sets
        )

    def _tie_break(self, winner: PlayerIdentifier) -> Self:
        pass
