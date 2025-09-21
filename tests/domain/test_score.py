import pytest

from app.domain.score import (
    PlayerIdentifier,
    Score,
    SetResult,
    TieBreakResult,
    TieBreakScore,
)

PointState = Score.PointState

NORMAL_POINT_CASES = [
    pytest.param(
        Score(),
        PlayerIdentifier.ONE,
        Score(points=(PointState.FIFTEEN, PointState.LOVE)),
        id='(Pts:0-0) | P1 wins -> (Pts:15-0)',
    ),
    pytest.param(
        Score(points=(PointState.FIFTEEN, PointState.FORTY)),
        PlayerIdentifier.ONE,
        Score(points=(PointState.THIRTY, PointState.FORTY)),
        id='(Pts:15-40) | P1 wins -> (Pts:30-40)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.FIFTEEN)),
        PlayerIdentifier.TWO,
        Score(points=(PointState.FORTY, PointState.THIRTY)),
        id='(Pts:40-15) | P2 wins -> (Pts:40-30)',
    ),
]


@pytest.mark.parametrize('initial_score, winner, expected_score', NORMAL_POINT_CASES)
def test_add_point_for_normal_point(
    initial_score: Score, winner: PlayerIdentifier, expected_score: Score
) -> None:
    assert initial_score.add_point(winner) == expected_score


GAME_POINT_CASES = [
    pytest.param(
        Score(points=(PointState.FORTY, PointState.THIRTY)),
        PlayerIdentifier.ONE,
        Score(points=(PointState.LOVE, PointState.LOVE), games=(1, 0)),
        id='(Pts:40-30) (Gms:0-0) | P1 wins -> (Pts:0-0) (Gms:1-0)',
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY)),
        PlayerIdentifier.TWO,
        Score(points=(PointState.LOVE, PointState.LOVE), games=(0, 1)),
        id='(Pts:30-40) (Gms:0-0) | P2 wins -> (Pts:0-0) (Gms:0-1)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.LOVE), games=(3, 3)),
        PlayerIdentifier.TWO,
        Score(points=(PointState.FORTY, PointState.FIFTEEN), games=(3, 3)),
        id='(Pts:40-0) (Gms:3-3) | P2 wins -> (Pts:40-15) (Gms:3-3)',
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY)),
        PlayerIdentifier.ONE,
        Score(points=(PointState.FORTY, PointState.FORTY), games=(0, 0)),
        id='(Pts:30-40) (Gms:0-0) | P1 wins -> (Pts:40-40) (Gms:0-0)',
    ),
]


@pytest.mark.parametrize('initial_score, winner, expected_score', GAME_POINT_CASES)
def test_add_point_for_game_point(
    initial_score: Score, winner: PlayerIdentifier, expected_score: Score
) -> None:
    assert initial_score.add_point(winner) == expected_score


DEUCE_ADVANTAGE_POINT_CASES = [
    pytest.param(
        Score(points=(PointState.FORTY, PointState.FORTY)),
        PlayerIdentifier.ONE,
        Score(points=(PointState.ADVANTAGE, PointState.FORTY)),
        id='(Pts:40-40) | P1 wins -> (Pts:AD-40)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.FORTY)),
        PlayerIdentifier.TWO,
        Score(points=(PointState.FORTY, PointState.ADVANTAGE)),
        id='(Pts:40-40) | P2 wins -> (Pts:40-AD)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.ADVANTAGE)),
        PlayerIdentifier.ONE,
        Score(points=(PointState.FORTY, PointState.FORTY)),
        id='(Pts:40-AD) | P1 wins -> (Pts:40-40)',
    ),
    pytest.param(
        Score(points=(PointState.ADVANTAGE, PointState.FORTY)),
        PlayerIdentifier.TWO,
        Score(points=(PointState.FORTY, PointState.FORTY)),
        id='(Pts:AD-40) | P2 wins -> (Pts:40-40)',
    ),
    pytest.param(
        Score(points=(PointState.ADVANTAGE, PointState.FORTY), games=(1, 1)),
        PlayerIdentifier.ONE,
        Score(games=(2, 1)),
        id='(Pts:AD-40) (Gms:1-1) | P1 wins -> (Pts:0-0) (Gms:2-1)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.ADVANTAGE), games=(1, 1)),
        PlayerIdentifier.TWO,
        Score(games=(1, 2)),
        id='(Pts:40-AD) (Gms:1-1) | P2 wins -> (Pts:0-0) (Gms:1-2)',
    ),
]


@pytest.mark.parametrize(
    'initial_score, winner, expected_score', DEUCE_ADVANTAGE_POINT_CASES
)
def test_add_point_for_deuce_advantage_point(
    initial_score: Score, winner: PlayerIdentifier, expected_score: Score
) -> None:
    assert initial_score.add_point(winner) == expected_score


SET_WIN_CASES = [
    pytest.param(
        Score(points=(PointState.FORTY, PointState.THIRTY), games=(5, 4)),
        PlayerIdentifier.ONE,
        Score(sets=(1, 0), finished_sets=(SetResult(games=(6, 4)),)),
        id='(Pts:40-30) (Gms:5-4) | P1 wins -> (Sts:1-0), finished_sets updated',
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY), games=(4, 5)),
        PlayerIdentifier.TWO,
        Score(sets=(0, 1), finished_sets=(SetResult(games=(4, 6)),)),
        id='(Pts:30-40) (Gms:4-5) | P2 wins -> (Sts:0-1), finished_sets updated',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.THIRTY), games=(5, 5), sets=(0, 1)),
        PlayerIdentifier.ONE,
        Score(games=(6, 5), sets=(0, 1)),
        id=(
            '(Pts:40-30) (Gms:5-5) (Sts:0-1) | P1 wins -> (Pts:0-0) (Gms:6-5) (Sts:0-1)'
        ),
    ),
]


@pytest.mark.parametrize('initial_score, winner, expected_score', SET_WIN_CASES)
def test_add_point_for_set_win(
    initial_score: Score, winner: PlayerIdentifier, expected_score: Score
) -> None:
    assert initial_score.add_point(winner) == expected_score


TIE_BREAK_CASES = [
    pytest.param(
        Score(points=(PointState.FORTY, PointState.THIRTY), games=(5, 6)),
        PlayerIdentifier.ONE,
        Score(games=(6, 6), tie_break_score=TieBreakScore()),
        id='(Pts:40-30) (Gms:5-6) | P1 wins -> (Pts:0-0) (Gms:6-6)',
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY), games=(6, 5)),
        PlayerIdentifier.TWO,
        Score(games=(6, 6), tie_break_score=TieBreakScore()),
        id='(Pts:30-40) (Gms:6-5) | P2 wins -> (Pts:0-0) (Gms:6-6)',
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore()),
        PlayerIdentifier.ONE,
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(1, 0))),
        id='(Pts:0-0) (Gms:6-6) | P1 wins -> (Pts:1-0) (Gms:6-6)',
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(6, 3))),
        PlayerIdentifier.ONE,
        Score(
            sets=(1, 0),
            finished_sets=(
                SetResult(games=(7, 6), tie_break=TieBreakResult(points=(7, 3))),
            ),
        ),
        id=(
            '(Pts:6-3) (Gms:6-6) (Sts: 0:0) '
            '| P1 wins -> (Sts: 1:0), finished_sets updated'
        ),
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(3, 6))),
        PlayerIdentifier.TWO,
        Score(
            sets=(0, 1),
            finished_sets=(
                SetResult(games=(6, 7), tie_break=TieBreakResult(points=(3, 7))),
            ),
        ),
        id=(
            '(Pts:3-6) (Gms:6-6) (Sts: 0:0) '
            '| P2 wins -> (Sts: 0:1), finished_sets updated'
        ),
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(5, 5))),
        PlayerIdentifier.ONE,
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(6, 5))),
        id='(Pts:5-5) (Gms:6-6) (Sts: 0:0) | P1 wins -> (Pts:6-5) (Gms:6-6) (Sts: 0:0)',
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(6, 6))),
        PlayerIdentifier.ONE,
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(7, 6))),
        id='(Pts:6-6) (Gms:6-6) (Sts: 0:0) | P1 wins -> (Pts:7-6) (Gms:6-6) (Sts: 0:0)',
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(7, 6))),
        PlayerIdentifier.ONE,
        Score(
            sets=(1, 0),
            finished_sets=(
                SetResult(games=(7, 6), tie_break=TieBreakResult(points=(8, 6))),
            ),
        ),
        id=(
            '(Pts:7-6) (Gms:6-6) (Sts: 0:0) '
            '| P1 wins -> (Sts: 1:0), , finished_sets updated'
        ),
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(7, 7))),
        PlayerIdentifier.ONE,
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(8, 7))),
        id='(Pts:7-7) (Gms:6-6) (Sts: 0:0) | P1 wins -> (Pts:8-7) (Gms:6-6) (Sts: 0:0)',
    ),
]


@pytest.mark.parametrize('initial_score, winner, expected_score', TIE_BREAK_CASES)
def test_add_point_for_tie_break(
    initial_score: Score, winner: PlayerIdentifier, expected_score: Score
) -> None:
    assert initial_score.add_point(winner) == expected_score


def test_initial_score_has_empty_finished_sets() -> None:
    assert Score().finished_sets == ()


FINISHED_SETS_UPDATE_CASES = [
    pytest.param(
        Score(
            sets=(0, 1),
            finished_sets=(SetResult(games=(5, 7), tie_break=None),),
            games=(5, 4),
            points=(PointState.FORTY, PointState.LOVE),
        ),
        PlayerIdentifier.ONE,
        (
            SetResult(games=(5, 7), tie_break=None),
            SetResult(games=(6, 4), tie_break=None),
        ),
        id=(
            '(Sts:0-1, finished_sets:1) (Gms:5-4, Pts:40-0) '
            '| P1 wins set -> finished_sets grows to 2'
        ),
    ),
    pytest.param(
        Score(
            sets=(1, 0),
            finished_sets=(SetResult(games=(6, 4), tie_break=None),),
            games=(6, 6),
            tie_break_score=TieBreakScore(points=(6, 7)),
        ),
        PlayerIdentifier.TWO,
        (
            SetResult(games=(6, 4), tie_break=None),
            SetResult(games=(6, 7), tie_break=TieBreakResult(points=(6, 8))),
        ),
        id=(
            '(Sts:1-0, finished_sets:1) (Gms:6-6, TB:6-7) '
            '| P2 wins set -> finished_sets grows to 2'
        ),
    ),
]


@pytest.mark.parametrize(
    'initial_score, winner, expected_finished_sets', FINISHED_SETS_UPDATE_CASES
)
def test_add_point_updates_finished_sets_correctly(
    initial_score: Score,
    winner: PlayerIdentifier,
    expected_finished_sets: tuple[SetResult, ...],
) -> None:
    final_score = initial_score.add_point(winner)
    assert final_score.finished_sets == expected_finished_sets
