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


# "Компонент Счета" - это атомарная часть счета, т.е. очки, геймы или сеты.
# Технически, это может быть либо PointState (для очков), либо int (для геймов/сетов).
TScoreComponent = TypeVar('TScoreComponent', 'Score.PointState', int)


@dataclass(frozen=True)
class TieBreakResult:
    points: tuple[int, int]


@dataclass(frozen=True)
class SetResult:
    games: tuple[int, int]
    tie_break: TieBreakResult | None = None


@dataclass(frozen=True)
class Score:
    class PointState(StrEnum):
        LOVE = '0'
        FIFTEEN = '15'
        THIRTY = '30'
        FORTY = '40'
        ADVANTAGE = 'AD'

    points: tuple[PointState, PointState] = (PointState.LOVE, PointState.LOVE)
    games: tuple[int, int] = (0, 0)
    sets: tuple[int, int] = (0, 0)

    tie_break_score: TieBreakScore | None = None

    finished_sets: tuple[SetResult, ...] = ()

    _NORMAL_POINT_TRANSITION: ClassVar[dict[PointState, PointState]] = {
        PointState.LOVE: PointState.FIFTEEN,
        PointState.FIFTEEN: PointState.THIRTY,
        PointState.THIRTY: PointState.FORTY,
    }

    _GAMES_TO_WIN_SET: ClassVar[int] = 6
    _GAMES_FOR_TIE_BREAK: ClassVar[tuple[int, int]] = (6, 6)
    _MIN_GAME_DIFFERENCE_FOR_SET_WIN: ClassVar[int] = 2

    def get_view_score_model(self) -> dict[str, str | int]:
        points = (
            self.points if self.tie_break_score is None else self.tie_break_score.points
        )
        return {
            'player1_points': points[PlayerIdentifier.ONE],
            'player1_games': self.games[PlayerIdentifier.ONE],
            'player1_sets': self.sets[PlayerIdentifier.ONE],
            'player2_points': points[PlayerIdentifier.TWO],
            'player2_games': self.games[PlayerIdentifier.TWO],
            'player2_sets': self.sets[PlayerIdentifier.TWO],
        }

    def add_point(self, winner: PlayerIdentifier) -> Self:
        if self.tie_break_score is not None:
            return self._handle_tie_break_point(winner)

        if self.PointState.ADVANTAGE in self.points or (
            self.points == (self.PointState.FORTY, self.PointState.FORTY)
        ):
            return self._handle_deuce_advantage_point(winner)

        if self.PointState.FORTY in self.points:
            return self._handle_game_point(winner)

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
        if self.points[winner] is self.PointState.FORTY:
            return self._win_game(winner)
        return self._handle_normal_point(winner)

    def _handle_deuce_advantage_point(self, winner: PlayerIdentifier) -> Self:
        if self.points == (self.PointState.FORTY, self.PointState.FORTY):
            opponent = winner.opponent
            opponent_points = self.points[opponent]
            winner_points = self.PointState.ADVANTAGE
            new_points = self._build_score_component_tuple(
                winner=winner,
                winner_score_component=winner_points,
                opponent_score_component=opponent_points,
            )
            return replace(self, points=new_points)

        if self.points[winner] is self.PointState.ADVANTAGE:
            return self._win_game(winner)

        return replace(self, points=(self.PointState.FORTY, self.PointState.FORTY))

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
            return self._win_set(winner=winner, final_games=new_games)

        if new_games == self._GAMES_FOR_TIE_BREAK:
            return replace(
                self,
                points=(self.PointState.LOVE, self.PointState.LOVE),
                games=new_games,
                tie_break_score=TieBreakScore(),
            )

        return replace(
            self, points=(self.PointState.LOVE, self.PointState.LOVE), games=new_games
        )

    def _win_set(
        self,
        winner: PlayerIdentifier,
        final_games: tuple[int, int],
        final_tie_break_points: TieBreakResult | None = None,
    ) -> Self:
        opponent = winner.opponent
        opponent_sets = self.sets[opponent]
        winner_sets = self.sets[winner] + 1
        new_sets = self._build_score_component_tuple(
            winner=winner,
            winner_score_component=winner_sets,
            opponent_score_component=opponent_sets,
        )

        tie_break_result = (
            final_tie_break_points if final_tie_break_points is not None else None
        )
        set_result = SetResult(games=final_games, tie_break=tie_break_result)
        new_finished_sets = self.finished_sets + (set_result,)

        return replace(
            self,
            points=(self.PointState.LOVE, self.PointState.LOVE),
            games=(0, 0),
            sets=new_sets,
            tie_break_score=None,
            finished_sets=new_finished_sets,
        )

    def _increment_game(self, winner: PlayerIdentifier) -> tuple[int, int]:
        opponent = winner.opponent
        opponent_games = self.games[opponent]
        winner_games = self.games[winner] + 1
        return self._build_score_component_tuple(
            winner=winner,
            winner_score_component=winner_games,
            opponent_score_component=opponent_games,
        )

    def _handle_tie_break_point(self, winner: PlayerIdentifier) -> Self:
        if self.tie_break_score is None:
            raise ValueError(
                'Не удается обработать тай-брейк-пойнт: счет не в режиме тай-брейка.'
            )
        new_tie_break_score = self.tie_break_score.add_point(winner)
        if new_tie_break_score.is_finished():
            final_games = self._increment_game(winner)
            final_tie_break_points = TieBreakResult(points=new_tie_break_score.points)
            return self._win_set(
                winner=winner,
                final_games=final_games,
                final_tie_break_points=final_tie_break_points,
            )
        return replace(self, tie_break_score=new_tie_break_score)


@dataclass(frozen=True)
class TieBreakScore:
    points: tuple[int, int] = (0, 0)

    _POINTS_TO_WIN_TIE_BREAK: ClassVar[int] = 7
    _MIN_POINT_DIFFERENCE_FOR_WIN: ClassVar[int] = 2

    def add_point(self, winner: PlayerIdentifier) -> Self:
        opponent = winner.opponent
        opponent_points = self.points[opponent]

        winner_points = self.points[winner] + 1

        new_points = (
            (winner_points, opponent_points)
            if winner is PlayerIdentifier.ONE
            else (opponent_points, winner_points)
        )
        return replace(self, points=new_points)

    def is_finished(self) -> bool:
        p_max = max(self.points)
        p_min = min(self.points)
        return (
            p_max >= self._POINTS_TO_WIN_TIE_BREAK
            and p_max - p_min >= self._MIN_POINT_DIFFERENCE_FOR_WIN
        )
