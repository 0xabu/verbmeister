from collections import defaultdict
import csv
import dataclasses
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass(frozen=True)
class VerbForm:
    infinitiv: str
    form: str

@dataclass(frozen=True)
class Question:
    verbform: VerbForm
    example: str
    english: str

MISSPELT_FILENAME = 'misspelt_verbs.csv'
MISSPELT_COUNT_FIELDNAME = 'correct_count'
MISSPELT_FIELDS = tuple(field.name for field in dataclasses.fields(VerbForm)) + (MISSPELT_COUNT_FIELDNAME,)

HIGHSCORE_FILENAME = 'high_scores.csv'
HIGHSCORE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class Game:
    def __init__(self) -> None:
        self.questions: list[Question] = []
        self.answers: dict[VerbForm, set[str]] = defaultdict(set)
        self.misspelt_verbs: dict[VerbForm, int]

        self.load_data()
        self.load_misspelt_verbs()

        # we start by repeating the misspelt verbs
        self.initial_questions: list[Question] = []
        for vf in self.misspelt_verbs.keys():
            self.initial_questions.extend(q for q in self.questions if vf == q.verbform)
        random.shuffle(self.initial_questions)

    def load_data(self) -> None:
        # Load the CSV file for the game data
        with open('table_data.csv', encoding='utf-8') as fh:
            for entry in csv.DictReader(fh):
                q = Question(VerbForm(entry['infinitiv'], entry['form']), entry['example'], entry['englisch'])

                # temporarily skip Konjunktiv II
                if not q.verbform.form.startswith('Konjunktiv'):
                    self.questions.append(q)
                    self.answers[q.verbform].add(entry['verb'])

    # Function to save misspelt verbs
    def save_misspelt_verbs(self) -> None:
        with open(MISSPELT_FILENAME, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, MISSPELT_FIELDS, extrasaction='ignore')
            writer.writeheader()
            for verb, count in self.misspelt_verbs.items():
                writer.writerow(dataclasses.asdict(verb) | {MISSPELT_COUNT_FIELDNAME: count})

    # Function to load misspelt verbs
    def load_misspelt_verbs(self) -> None:
        self.misspelt_verbs = {}
        try:
            with open(MISSPELT_FILENAME, 'r', encoding='utf-8', newline='') as file:
                for row in csv.DictReader(file):
                    count = int(row.pop(MISSPELT_COUNT_FIELDNAME))
                    self.misspelt_verbs[VerbForm(**row)] = count
        except FileNotFoundError:
            pass  # No file to load, continue with an empty dict

    def get_next_question(self) -> Question:
        try:
            return self.initial_questions.pop()
        except IndexError:
            return random.choice(self.questions)

    def submit_answer(self, vf: VerbForm, player_answer: str) -> tuple[bool, set[str]]:
        need_save = False
        correct_answers = self.answers[vf]
        if is_correct := player_answer.lower() in correct_answers:
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
        with open(HIGHSCORE_FILENAME, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for name, (score, timestamp) in sorted_scores:
                writer.writerow((name, score, timestamp))

    # Function to load high scores
    def load(self) -> None:
        self.scores = {}
        try:
            with open(HIGHSCORE_FILENAME, 'r', encoding='utf-8', newline='') as file:
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
        name_length = min(14, max(4, max(len(name) for name in self.scores.keys())))
        line_format = "{:<" + str(name_length) + ".14}  {:>6}  {:>6}"
        lines = [line_format.format("Name", "Punkte", "Datum")]  # Header

        # Sort and limit to top 10 scores
        top_scores = sorted(self.scores.items(), key=lambda x: x[1][0], reverse=True)[:10]

        for name, (high_score, timestamp) in top_scores:
            date = datetime.strptime(timestamp, HIGHSCORE_DATE_FORMAT).strftime("%b %d")
            lines.append(line_format.format(name, high_score, date))

        return '\n'.join(lines)
