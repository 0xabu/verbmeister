import csv
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass(frozen=True)
class Question:
    infinitiv: str
    form: str
    verb: str

# Function definitions (save_misspelt_verbs, load_misspelt_verbs, save_high_scores, load_high_scores, parse_timestamp, is_correct_answer)

# Function to save misspelt verbs, shuffled
def save_misspelt_verbs(filename='misspelt_verbs.csv'):
    misspelt_items = list(misspelt_verbs.items())
    random.shuffle(misspelt_items)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Infinitiv', 'Form', 'Verb', 'CorrectCount'])
        for (infinitiv, form), data in misspelt_items:
            writer.writerow([infinitiv, form, data['Verb'], data['CorrectCount']])

# Function to load misspelt verbs
def load_misspelt_verbs(filename='misspelt_verbs.csv'):
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                infinitiv, form, verb, correct_count = row
                misspelt_verbs[(infinitiv, form)] = {'Verb': verb, 'CorrectCount': int(correct_count)}
    except FileNotFoundError:
        pass  # No file to load, continue with an empty list

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

# Function to check if the answer is correct
def is_correct_answer(player_answer, correct_answers):
    return player_answer.lower() in [verb.lower() for verb in correct_answers]

def get_correct_answers(data, infinitiv, form):
    # Pandas version: data[(data['Infinitiv'] == infinitiv) & (data['Form'] == form)]['Verb'].unique()
    return set([d.verb for d in data if d.infinitiv == infinitiv and d.form == form])


# Load the CSV file for the game data
df: list[Question] = []
with open('table_data.csv') as fh:
    for entry in csv.DictReader(fh):
        df.append(Question(**entry))

# Initialize high scores and misspelt verbs
high_scores = load_high_scores()
misspelt_verbs = {}
load_misspelt_verbs()

# Game setup
lives = 3
score = 0

# Start of the game loop
while lives > 0:
    # Use a list of keys to iterate over to avoid RuntimeError
    for (infinitiv, form) in list(misspelt_verbs.keys()):
        # Find all correct verbs for the given infinitiv and form
        correct_verbs = get_correct_answers(df, infinitiv, form)

        # Ask the player and ensure they provide a non-empty answer
        player_answer = ""
        while not player_answer.strip():
            print(f"\n{infinitiv}")
            player_answer = input(f"{form} ").strip()

        # Check the answer
        if is_correct_answer(player_answer, correct_verbs):
            score += 1
            print("Richtig! Punktestand:", score)
            # Update misspelt_verbs if correct
            if (infinitiv, form) in misspelt_verbs:
                misspelt_verbs[(infinitiv, form)]['CorrectCount'] += 1
                if misspelt_verbs[(infinitiv, form)]['CorrectCount'] >= 7:
                    del misspelt_verbs[(infinitiv, form)]
        else:
            lives -= 1
            print(f"Falsch! Richtige Antworten enthalten: {'/'.join(correct_verbs)}. Du hast nur noch {lives} Leben!")
            # Update misspelt_verbs if wrong
            misspelt_verbs[(infinitiv, form)] = {'Verb': '/'.join(correct_verbs), 'CorrectCount': 0}

        # Check if the verb should be removed from the misspelt list
        if misspelt_verbs.get((infinitiv, form), {}).get('CorrectCount', 0) >= 7:
            del misspelt_verbs[(infinitiv, form)]

        if lives <= 0:
            break

        

    # Continue with new random verbs from the full list
    while lives > 0:
        # Randomly select a row from the dataframe
        row = random.choice(df)
        correct_verbs = get_correct_answers(df, row.infinitiv, row.form)

        # Ask the player and ensure they provide a non-empty answer
        player_answer = ""
        while not player_answer.strip():
            print(f"\n{row.infinitiv}")
            player_answer = input(f"{row.form} ").strip()

        # Check the answer
        if is_correct_answer(player_answer, correct_verbs):
            score += 1
            print("Richtig! Punktestand:", score)
            # Update misspelt_verbs if correct
            if (row.infinitiv, row.form) in misspelt_verbs:
                misspelt_verbs[(row.infinitiv, row.form)]['CorrectCount'] += 1
                if misspelt_verbs[(row.infinitiv, row.form)]['CorrectCount'] >= 7:
                    del misspelt_verbs[(row.infinitiv, row.form)]
        else:
            lives -= 1
            print(f"Falsch! Richtige Antworten enthalten: {'/'.join(correct_verbs)}. Du hast nur noch {lives} Leben!")
            # Update misspelt_verbs if wrong
            misspelt_verbs[(row.infinitiv, row.form)] = {'Verb': '/'.join(correct_verbs), 'CorrectCount': 0}

        if lives <= 0:
            break
 

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
save_misspelt_verbs()
