import pytest
from server.game import Game, Answer, GamePhase


def test_new_game_starts_waiting():
    game = Game()

    assert game.state.phase == GamePhase.WAITING
    assert game.state.question is None
    assert game.state.answers == []
    assert game.state.strikes == 0

def test_start_round():
    game = Game()
    answers = [Answer(text="Answer 1", points=10), Answer(text="Answer 2", points=20)]
    game.start_round("Sample Question", answers)

    assert game.state.phase == GamePhase.QUESTION
    assert game.state.question == "Sample Question"
    assert game.state.answers == answers
    assert game.state.strikes == 0
    assert game.state.buzzing_team is None

def test_team_can_buzz_during_question_phase():
    game = Game()
    answers = [Answer(text="Answer 1", points=10), Answer(text="Answer 2", points=20)]
    game.start_round("Sample Question", answers)

    game.buzz("Team A")

    assert game.state.phase == GamePhase.BUZZING
    assert game.state.buzzing_team == "Team A"

def test_team_cannot_buzz_before_round_starts():
    game = Game()

    with pytest.raises(ValueError):
        game.buzz("Team A")

def test_team_can_submit_answer_after_buzzing():
    game = Game()
    answers = [Answer(text="Answer 1", points=10), Answer(text="Answer 2", points=20)]
    game.start_round("Sample Question", answers)
    game.buzz("Team A")

    game.submit_answer("Answer 1")

    assert game.state.phase == GamePhase.ANSWERING
    assert game.state.answers[0].revealed is True
    assert game.state.answers[1].revealed is False

def test_team_cannot_submit_answer_before_buzzing():
    game = Game()
    answers = [Answer(text="Answer 1", points=10), Answer(text="Answer 2", points=20)]
    game.start_round("Sample Question", answers)

    with pytest.raises(ValueError):
        game.submit_answer("Answer 1")

def test_team_cannot_submit_nonexistent_answer():
    game = Game()
    answers = [Answer(text="Answer 1", points=10), Answer(text="Answer 2", points=20)]
    game.start_round("Sample Question", answers)
    game.buzz("Team A")

    with pytest.raises(ValueError):
        game.submit_answer("Nonexistent Answer")

def test_add_strike():
    game = Game()

    game.start_round("Sample Question", [Answer(text="Answer 1", points=10)])
    game.buzz("Team A")
    game.add_strike()

    assert game.state.strikes == 1
    assert game.state.phase == GamePhase.BUZZING

    game.add_strike()

    assert game.state.strikes == 2
    assert game.state.phase == GamePhase.BUZZING

    game.add_strike()

    assert game.state.strikes == 3
    assert game.state.phase == GamePhase.BUZZING

def test_cannot_add_strike_before_buzzing():
    game = Game()

    with pytest.raises(ValueError):
        game.add_strike()