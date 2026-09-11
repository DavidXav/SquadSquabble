import pytest
from server.game import Game, Answer, GamePhase, Team


def test_buzz_starts_face_off():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    assert game.state.phase == GamePhase.FACE_OFF
    assert game.state.first_buzzing_team == "Team A"

    
def test_first_team_submits_face_off_answer():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")

    assert game.state.first_buzzing_team_score == 30
    assert game.state.phase == GamePhase.FACE_OFF
    assert game.state.round_total_score == 30
    assert game.state.answers[0].revealed is True

def test_second_team_submits_face_off_answer():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    assert game.state.second_buzzing_team == "Team B"
    assert game.state.second_buzzing_team_score == 20
    assert game.state.phase == GamePhase.ANSWERING

def test_first_team_wins_face_off():
    game = Game()

    game.state.teams = [
        Team(name="Team A"),
        Team(name="Team B"),
    ]

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    assert game.state.answering_team == "Team A"
    assert game.state.phase == GamePhase.ANSWERING

def test_second_team_wins_face_off():
    game = Game()

    game.state.teams = [
        Team(name="Team A"),
        Team(name="Team B"),
    ]

    answers = [
        Answer(text="Dogs", points=20),
        Answer(text="Cats", points=30),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    assert game.state.answering_team == "Team B"
    assert game.state.phase == GamePhase.ANSWERING

def test_face_off_answers_add_to_round_total():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    assert game.state.round_total_score == 50

def test_cannot_submit_face_off_answer_before_buzz():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
    ]

    game.start_round("Name an animal", answers)

    with pytest.raises(ValueError):
        game.submit_face_off_answer("Team A", "Dogs")

def test_face_off_answer_not_found():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    with pytest.raises(ValueError, match="Answer not found"):
        game.submit_face_off_answer("Team A", "Elephant")

def test_face_off_answer_not_found():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    with pytest.raises(ValueError, match="Answer not found"):
        game.submit_face_off_answer("Team A", "Elephant")

def test_cannot_submit_revealed_face_off_answer():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")

    with pytest.raises(ValueError, match="Answer already revealed"):
        game.submit_face_off_answer("Team B", "Dogs")

def test_cannot_submit_revealed_face_off_answer():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")

    with pytest.raises(ValueError, match="Answer already revealed"):
        game.submit_face_off_answer("Team B", "Dogs")

def test_first_team_cannot_submit_twice():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
        Answer(text="Birds", points=10),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")

    with pytest.raises(ValueError, match="First team has already submitted"):
        game.submit_face_off_answer("Team A", "Cats")

def test_cannot_submit_face_off_answer_after_face_off():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
        Answer(text="Birds", points=10),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    with pytest.raises(ValueError, match="not in face-off phase"):
        game.submit_face_off_answer("Team C", "Birds")

def test_submit_correct_answer():
    game = Game()

    game.state.teams = [
        Team(name="Team A"),
        Team(name="Team B"),
    ]

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
        Answer(text="Birds", points=10),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    game.submit_answer("Birds")

    assert game.state.answers[2].revealed is True
    assert game.state.round_total_score == 60

def test_three_strikes_starts_steal():
    game = Game()

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    game.add_strike()
    assert game.state.strikes == 1
    assert game.state.phase == GamePhase.ANSWERING

    game.add_strike()
    assert game.state.strikes == 2
    assert game.state.phase == GamePhase.ANSWERING

    game.add_strike()
    assert game.state.strikes == 3
    assert game.state.phase == GamePhase.STEAL

def test_correct_steal_awards_points():
    game = Game()

    game.state.teams = [
        Team(name="Team A"),
        Team(name="Team B"),
    ]

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
        Answer(text="Birds", points=10),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    # This will eventually put us in STEAL
    game.add_strike()
    game.add_strike()
    game.add_strike()

    game.steal_answer_correct("Team B", "Birds")

    assert game.state.phase == GamePhase.ROUND_END
    assert game.state.teams[1].score == 60

def test_incorrect_steal_awards_points_to_answering_team():
    game = Game()

    game.state.teams = [
        Team(name="Team A"),
        Team(name="Team B"),
    ]

    answers = [
        Answer(text="Dogs", points=30),
        Answer(text="Cats", points=20),
        Answer(text="Birds", points=10),
    ]

    game.start_round("Name an animal", answers)
    game.buzz("Team A")

    game.submit_face_off_answer("Team A", "Dogs")
    game.submit_face_off_answer("Team B", "Cats")

    game.add_strike()
    game.add_strike()
    game.add_strike()

    game.steal_answer_incorrect()

    assert game.state.phase == GamePhase.ROUND_END
    assert game.state.teams[0].score == 50