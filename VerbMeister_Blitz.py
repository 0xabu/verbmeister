import csv
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass(frozen=True)
class VerbForm:
    infinitiv: str
    form: str

@dataclass(frozen=True)
class Solution(VerbForm):
    verb: str

@dataclass
class MisspeltVerb:
    verb: str
    correct_count: int = 0

class Game:
    def __init__(self):
        self.problems: list[Solution]
        self.misspelt_verbs: dict[VerbForm, MisspeltVerb]

        self.load_problems()
        self.load_misspelt_verbs()

        # we start by repeating the misspelt verbs
        self.initial_questions: list[VerbForm] = list(self.misspelt_verbs.keys())

    def load_problems(self) -> None:
        # Load the CSV file for the game data
        self.problems = []
        with open('table_data.csv') as fh:
            for entry in csv.DictReader(fh):
                self.problems.append(Solution(**entry))

    # Function to save misspelt verbs, shuffled
    def save_misspelt_verbs(self, filename='misspelt_verbs.csv') -> None:
        misspelt_items = list(self.misspelt_verbs.items())
        random.shuffle(misspelt_items)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Infinitiv', 'Form', 'Verb', 'CorrectCount'])
            for verb, misspelt in misspelt_items:
                writer.writerow([verb.infinitiv, verb.form, misspelt.verb, misspelt.correct_count])

    # Function to load misspelt verbs
    def load_misspelt_verbs(self, filename='misspelt_verbs.csv') -> None:
        self.misspelt_verbs = {}
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    infinitiv, form, verb, correct_count = row
                    self.misspelt_verbs[VerbForm(infinitiv, form)] = MisspeltVerb(verb, int(correct_count))
        except FileNotFoundError:
            pass  # No file to load, continue with an empty dict

    def get_next_question(self) -> VerbForm:
        try:
            return self.initial_questions.pop()
        except IndexError:
            return random.choice(self.problems)

    def submit_answer(self, vf: VerbForm, player_answer: str) -> tuple[bool, set[str]]:
        correct_answers = set(p.verb for p in self.problems if p.infinitiv == vf.infinitiv and p.form == vf.form)
        if correct := player_answer.lower() in [verb.lower() for verb in correct_answers]:
            if vf in self.misspelt_verbs:
                if self.misspelt_verbs[vf].correct_count > 5:
                    del self.misspelt_verbs[vf]
                else:
                    self.misspelt_verbs[vf].correct_count += 1
        else: # wrong
            self.misspelt_verbs[vf] = MisspeltVerb('/'.join(correct_answers))

        return correct, correct_answers

# Function to save high scores, sorted from highest to lowest
def save_high_scores(scores, filename='high_scores.csv'):
    sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
    with open(filename, 'w') as file:
        for name, (score, timestamp) in sorted_scores:
            file.write(f"{name},{score},{timestamp}\n")

# Function to load high scores
def load_high_scores(filename='high_scores.csv'):
    scores = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                name, score, timestamp = line.strip().split(',')
                scores[name] = (int(score), timestamp)
    except FileNotFoundError:
        pass  # No file to load, start with empty scores
    return scores

# Function to parse timestamp with multiple possible formats
def parse_timestamp(timestamp_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Timestamp format not recognized: {timestamp_str}")

def main() -> None:
    game = Game()

    # Initialize high scores
    high_scores = load_high_scores()

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
            player_answer = input(f"{vf.form} ").strip()

        # Check the answer
        ok, correct_verbs = game.submit_answer(player_answer)
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
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        high_scores[player_name] = max((score, current_timestamp), high_scores.get(player_name, (0, '')), key=lambda x: x[0])
        save_high_scores(high_scores)

    # Display high scores
    max_name_length = max(len(name) for name in high_scores.keys())
    print("\nHigh Scores:")
    header_format = "{:<" + str(max_name_length) + "} {:>10} {:>15}"
    print(header_format.format("Name", "Score", "Date"))  # Header

    # Sort and limit to top 10 scores
    top_scores = sorted(high_scores.items(), key=lambda x: x[1][0], reverse=True)[:10]

    for name, (high_score, timestamp) in top_scores:
        date = parse_timestamp(timestamp).strftime("%b %d")
        line_format = "{:<" + str(max_name_length) + "} {:>10} {:>15}"
        print(line_format.format(name, high_score, date))
        
    # Save misspelt verbs at the end of the game
    game.save_misspelt_verbs()

if __name__ == "__main__":
    main()
