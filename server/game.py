from enum import Enum
from pydantic import BaseModel

class GamePhase(str, Enum):
    WAITING = "waiting"
    QUESTION = "question"
    BUZZING = "buzzing"
    FACE_OFF = "face_off"
    ANSWERING = "answering"
    STEAL = "steal"
    ROUND_END = "round_end"
    GAME_END = "game_end"

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
    first_buzzing_team: str | None = None
    first_buzzing_team_score: int = 0
    second_buzzing_team: str | None = None
    second_buzzing_team_score: int = 0

    answering_team: str | None = None
    stealing_team: str | None = None

    round_total_score: int = 0


class Game:
    def __init__(self):
        self.state = GameState()

    def start_round(self, question: str, answers: list[Answer]):
        self.state.phase = GamePhase.QUESTION
        self.state.question = question
        self.state.answers = answers
        self.state.strikes = 0
        self.state.first_buzzing_team = None
        self.state.second_buzzing_team = None
        self.state.first_buzzing_team_score = -1
        self.state.second_buzzing_team_score = -1

        self.state.round_total_score = 0

    def buzz(self, team: str):
        if self.state.phase != GamePhase.QUESTION:
            raise ValueError("Cannot buzz when not in question phase")
        
        self.state.phase = GamePhase.FACE_OFF
        self.state.first_buzzing_team = team
        self.state.second_buzzing_team = None
    
    def submit_face_off_answer(self, team: str, answer_text: str):
        if self.state.phase != GamePhase.FACE_OFF:
            raise ValueError("Cannot submit face-off answer when not in face-off phase")

        answer = next((a for a in self.state.answers if a.text == answer_text), None)

        if not answer:
            raise ValueError("Answer not found")

        if answer.revealed:
            raise ValueError("Answer already revealed")

        # First team is the team that buzzed
        if self.state.first_buzzing_team_score == -1:
            if team != self.state.first_buzzing_team:
                raise ValueError("First face-off answer must come from buzzing team")

            self.state.first_buzzing_team_score = answer.points

        # Second team answers
        else:
            if team == self.state.first_buzzing_team:
                raise ValueError("First team has already submitted a face-off answer")

            self.state.second_buzzing_team = team
            self.state.second_buzzing_team_score = answer.points

            # Determine who wins the face-off
            if self.state.first_buzzing_team_score > self.state.second_buzzing_team_score:
                self.state.answering_team = self.state.first_buzzing_team
            else:
                self.state.answering_team = self.state.second_buzzing_team

            self.state.phase = GamePhase.ANSWERING

        self.state.round_total_score += answer.points
        answer.revealed = True
    
    def start_answering(self, team: str):
        if self.state.phase != GamePhase.ANSWERING:
            raise ValueError("Cannot start answering when not in answering phase")
        
        self.state.answering_team = team


    def submit_answer(self, answer_text: str):
        if self.state.phase != GamePhase.ANSWERING:
            raise ValueError("Cannot submit answer when not answering")
        
        answer = next((a for a in self.state.answers if a.text == answer_text), None)
        if not answer:
            raise ValueError("Answer not found")
        
        if answer.revealed:
            raise ValueError("Answer already revealed")
        
        
        answer.revealed = True
        self.state.round_total_score += answer.points
        # if all answers are revealed, end the round and give points
        if all(a.revealed for a in self.state.answers):
            self.state.phase = GamePhase.ROUND_END
            for team in self.state.teams:
                if team.name == self.state.answering_team:
                    team.score += self.state.round_total_score
            self.state.phase = GamePhase.ROUND_END


    def reveal_answer(self, answer_text: str):
        answer = next((a for a in self.state.answers if a.text == answer_text), None)
        if not answer:
            raise ValueError("Answer not found")
        
        if answer.revealed:
            raise ValueError("Answer already revealed")
        
        answer.revealed = True

    def add_strike(self):
        if self.state.phase != GamePhase.ANSWERING:
            raise ValueError("Cannot add strike")

        self.state.strikes += 1

        if self.state.strikes == 3:
            self.state.phase = GamePhase.STEAL
    
    def steal_answer_correct(self, team: str, answer_text: str):
        if self.state.phase != GamePhase.STEAL:
            raise ValueError("Cannot steal answer when not in steal phase")
        
        answer = next((a for a in self.state.answers if a.text == answer_text), None)
        if not answer:
            raise ValueError("Answer not found")
        
        if answer.revealed:
            raise ValueError("Answer already revealed")
        
        self.state.round_total_score += answer.points
        self.state.stealing_team = team
        answer.revealed = True
        for team in self.state.teams:
            if team.name == self.state.stealing_team:
                team.score += self.state.round_total_score
        self.state.phase = GamePhase.ROUND_END

    def steal_answer_incorrect(self):
        if self.state.phase != GamePhase.STEAL:
            raise ValueError("Cannot steal answer when not in steal phase")
        
        for team in self.state.teams:
            if team.name == self.state.answering_team:
                team.score += self.state.round_total_score

        self.state.phase = GamePhase.ROUND_END
    
    def end_round(self):
        self.state.phase = GamePhase.ROUND_END