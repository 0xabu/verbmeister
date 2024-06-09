from core import Game, HighScores

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
