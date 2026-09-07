from enum import Enum
from pydantic import BaseModel

class GamePhase(str, Enum):
    WAITING = "waiting"
    QUESTION = "question"
    BUZZING = "buzzing"
    ANSWERING = "answering"
    ROUND_END = "round_end"
    GANE_END = "game_end"

class Answer(BaseModel):
    text: str
    points: int
    revealed: bool = False

class Team(BaseModel):
    name: str
    score: int = 0

class GameState(BaseModel):
    phase: GamePhase = GamePhase.WAITING
    question: str | None = None

    answers: list[Answer] = []

    teams: list[Team] = []

    strikes: int = 0
    buzzing_team: str | None = None


class Game:
    def __init__(self):
        self.state = GameState()

    def start_round(self, question: str, answers: list[Answer]):
        self.state.phase = GamePhase.QUESTION
        self.state.question = question
        self.state.answers = answers
        self.state.strikes = 0
        self.state.buzzing_team = None