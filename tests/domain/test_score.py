import pytest

from app.domain.score import PlayerIdentifier, Score, TieBreakScore

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
        Score(sets=(1, 0)),
        id='(Pts:40-30) (Gms:5-4) | P1 wins -> (Pts:0-0) (Gms:0-0) (Sts:1-0)',
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY), games=(4, 5)),
        PlayerIdentifier.TWO,
        Score(sets=(0, 1)),
        id='(Pts:30-40) (Gms:4-5) | P2 wins -> (Pts:0-0) (Gms:0-0) (Sts:0-1)',
    ),
    pytest.param(
        Score(points=(PointState.FORTY, PointState.THIRTY), games=(6, 5), sets=(0, 1)),
        PlayerIdentifier.ONE,
        Score(sets=(1, 1)),
        id=(
            '(Pts:40-30) (Gms:6-5) (Sts:0-1) | P1 wins -> (Pts:0-0) (Gms:0-0) (Sts:1-1)'
        ),
    ),
    pytest.param(
        Score(points=(PointState.THIRTY, PointState.FORTY), games=(5, 6), sets=(1, 0)),
        PlayerIdentifier.TWO,
        Score(sets=(1, 1)),
        id=(
            '(Pts:30-40) (Gms:5-6) (Sts:1-0) '
            '| P2 wins -> (Pts:0-00) (Gms:0-0) (Sts:1-1)'
        ),
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
        Score(sets=(1, 0)),
        id='(Pts:6-3) (Gms:6-6) (Sts: 0:0) | P1 wins -> (Pts:0-0) (Gms:0-0) (Sts: 1:0)',
    ),
    pytest.param(
        Score(games=(6, 6), tie_break_score=TieBreakScore(points=(3, 6))),
        PlayerIdentifier.TWO,
        Score(sets=(0, 1)),
        id='(Pts:3-6) (Gms:6-6) (Sts: 0:0) | P2 wins -> (Pts:0-0) (Gms:0-0) (Sts: 0:1)',
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
        Score(sets=(1, 0)),
        id='(Pts:7-6) (Gms:6-6) (Sts: 0:0) | P1 wins -> (Pts:0-0) (Gms:0-0) (Sts: 1:0)',
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
