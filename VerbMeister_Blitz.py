import csv
import dataclasses
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass(frozen=True)
class VerbForm:
    infinitiv: str
    form: str
    example: str

@dataclass(frozen=True)
class Solution(VerbForm):
    verb: str

MISSPELT_FILENAME = 'misspelt_verbs.csv'
MISSPELT_COUNT_FIELDNAME = 'correct_count'
MISSPELT_FIELDS = tuple(field.name for field in dataclasses.fields(VerbForm)) + (MISSPELT_COUNT_FIELDNAME,)

HIGHSCORE_FILENAME = 'high_scores.csv'
HIGHSCORE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class Game:
    def __init__(self) -> None:
        self.problems: list[Solution]
        self.misspelt_verbs: dict[VerbForm, int]

        self.load_problems()
        self.load_misspelt_verbs()

        # we start by repeating the misspelt verbs
        self.initial_questions = list(self.misspelt_verbs.keys())
        random.shuffle(self.initial_questions)

    def load_problems(self) -> None:
        # Load the CSV file for the game data
        self.problems = []
        with open('table_data.csv') as fh:
            for entry in csv.DictReader(fh):
                self.problems.append(Solution(**entry))

    # Function to save misspelt verbs
    def save_misspelt_verbs(self) -> None:
        with open(MISSPELT_FILENAME, 'w') as file:
            writer = csv.DictWriter(file, MISSPELT_FIELDS, extrasaction='ignore')
            writer.writeheader()
            for verb, count in self.misspelt_verbs.items():
                writer.writerow(dataclasses.asdict(verb) | {MISSPELT_COUNT_FIELDNAME: count})

    # Function to load misspelt verbs
    def load_misspelt_verbs(self) -> None:
        self.misspelt_verbs = {}
        try:
            with open(MISSPELT_FILENAME, 'r') as file:
                for row in csv.DictReader(file):
                    count = int(row.pop(MISSPELT_COUNT_FIELDNAME))
                    self.misspelt_verbs[VerbForm(**row)] = count
        except FileNotFoundError:
            pass  # No file to load, continue with an empty dict

    def get_next_question(self) -> VerbForm:
        try:
            return self.initial_questions.pop()
        except IndexError:
            return random.choice(self.problems)

    def submit_answer(self, vf: VerbForm, player_answer: str) -> tuple[bool, set[str]]:
        need_save = False
        correct_answers = set(p.verb for p in self.problems if p.infinitiv == vf.infinitiv and p.form == vf.form)
        if is_correct := player_answer.lower() in [verb.lower() for verb in correct_answers]:
            if vf in self.misspelt_verbs:
                if self.misspelt_verbs[vf] > 5:
                    del self.misspelt_verbs[vf]
                else:
                    self.misspelt_verbs[vf] += 1
                need_save = True
        else: # wrong
            self.misspelt_verbs[vf] = 0
            need_save = True

        if need_save:
            self.save_misspelt_verbs()

        return is_correct, correct_answers

class HighScores:
    def __init__(self) -> None:
        self.scores: dict[str, tuple[int, str]]
        self.load()

    # Function to save high scores, sorted from highest to lowest
    def save(self) -> None:
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1][0], reverse=True)
        with open(HIGHSCORE_FILENAME, 'w') as file:
            writer = csv.writer(file)
            for name, (score, timestamp) in sorted_scores:
                writer.writerow((name, score, timestamp))

    # Function to load high scores
    def load(self) -> None:
        self.scores = {}
        try:
            with open(HIGHSCORE_FILENAME, 'r') as file:            
                for name, score, timestamp in csv.reader(file):
                    self.scores[name] = (int(score), timestamp)
        except FileNotFoundError:
            pass  # No file to load, start with empty scores

    def update(self, name: str, score: int) -> None:
        if name not in self.scores or self.scores[name][0] < score:
            self.scores[name] = (score, datetime.now().strftime(HIGHSCORE_DATE_FORMAT))
            self.save()

    def format(self) -> str:
        # Format high scores
        max_name_length = max(len(name) for name in self.scores.keys())
        header_format = "{:<" + str(max_name_length) + "} {:>10} {:>15}"
        lines = [header_format.format("Name", "Punkte", "Datum")]  # Header

        # Sort and limit to top 10 scores
        top_scores = sorted(self.scores.items(), key=lambda x: x[1][0], reverse=True)[:10]

        for name, (high_score, timestamp) in top_scores:
            date = datetime.strptime(timestamp, HIGHSCORE_DATE_FORMAT).strftime("%b %d")
            line_format = "{:<" + str(max_name_length) + "} {:>10} {:>15}"
            lines.append(line_format.format(name, high_score, date))

        return '\n'.join(lines)

def main() -> None:
    game = Game()

    # Initialize high scores
    high_scores = HighScores()

    # Game setup
    lives = 3
    score = 0

    # Start of the game loop
    while lives > 0:
        vf = game.get_next_question()

        # Ask the player and ensure they provide a non-empty answer
        player_answer = ""
        while not player_answer.strip():
            print(f"\n{vf.infinitiv}")
            player_answer = input(f"{vf.form} Ez. {vf.example} ").strip()

        # Check the answer
        ok, correct_verbs = game.submit_answer(vf, player_answer)
        if ok:
            score += 1
            print("Richtig! Punktestand:", score)
        else:
            lives -= 1
            print(f"Falsch! Richtige Antworten enthalten: {'/'.join(correct_verbs)}. Du hast nur noch {lives} Leben!")

    # Game over logic
    print("\nDas Spiel ist aus! Dein Punktestand ist:", score)

    # Check if this is a high score and handle saving
    if score > 0:
        player_name = input("Gib deinen Namen ein, um deinen Punktestand zu speichern: ")
        high_scores.update(player_name, score)

    # Display high scores
    print("\nHigh Scores:" + high_scores.format())

if __name__ == "__main__":
    main()
