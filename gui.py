import platform
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from typing import Optional

from core import Game, HighScores

class GameOverDialog(simpledialog.Dialog):
    def __init__(self, score: int, parent: Optional[tk.Misc] = None) -> None:
        self.score = score
        super().__init__(parent, title="Spiel aus!")

    def body(self, frame: tk.Frame) -> tk.Misc | None:
        ttk.Label(frame, text="Das Spiel ist aus!").grid(column=0, row=0, columnspan=2)
        ttk.Label(frame, text=f"Punktestand: {self.score}").grid(column=0, row=1, columnspan=2)

        self.name = tk.StringVar()

        if self.score:
            ttk.Label(frame, text="Name für High Score:").grid(column=0, row=2)
            entry = ttk.Entry(frame, width=7, textvariable=self.name)
            entry.grid(column=1, row=2)
            return entry
        else:
            return None

    def validate(self):
        if self.score:
            name = self.name.get()
            if name:
                self.result = name
                return True
            else:
                messagebox.showwarning(message="Name war leer")
                return False

class HighScoreDialog(simpledialog.Dialog):
    def __init__(self, text: str, parent: Optional[tk.Misc] = None) -> None:
        self.hstext = text
        super().__init__(parent, title="High Scores")

    def body(self, frame: tk.Frame) -> None:
        t = tk.Text(frame, font='TkFixedFont', width=30, height=11, wrap="none")
        t.insert('end', self.hstext)
        t.config(state='disabled')
        t.grid()

    def buttonbox(self) -> None:
        box = ttk.Frame(self)
        b = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        b.focus()
        b.pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Windows UI scaling
        if platform.system() == 'Windows':
            self.tk.call('tk', 'scaling', 1.5)

        self.title("VerbMeister Blitz")

        self.game = Game()
        self.highscores = HighScores()

        self.verb = tk.StringVar()
        self.verbform = tk.StringVar()
        self.translation = tk.StringVar()
        self.question = tk.StringVar()
        self.input = tk.StringVar()
        self.button_label = tk.StringVar()
        self.response = tk.StringVar()
        self.points = tk.IntVar()
        self.lives = tk.IntVar()

        headerframe = ttk.Frame(self)
        headerframe.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        headerframe.grid_columnconfigure(2, weight=1)

        ttk.Label(headerframe, text='Punkte:', font='TkHeadingFont').grid(row=0, column=0, sticky=tk.E)
        ttk.Label(headerframe, textvariable=self.points, foreground='blue').grid(row=0, column=1, sticky=tk.W)

        ttk.Label(headerframe, text='Leben:', font='TkHeadingFont').grid(row=0, column=3, sticky=tk.E)
        ttk.Label(headerframe, textvariable=self.lives, foreground='red').grid(row=0, column=4, sticky=tk.W)

        bodyframe = ttk.Frame(self)
        bodyframe.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        bodyframe.grid_columnconfigure([0,1], weight=1)

        ttk.Label(bodyframe, textvariable=self.verb, font=('TkDefaultFont', 16)).grid(row=0, column=0, columnspan=2, padx=5, pady=2)
        ttk.Label(bodyframe, textvariable=self.translation).grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        ttk.Label(bodyframe, textvariable=self.verbform).grid(row=2, column=0, columnspan=2)

        ttk.Label(bodyframe, textvariable=self.question).grid(row=3, column=0, sticky=tk.E, pady=10)
        self.input_entry = ttk.Entry(bodyframe, width=7, textvariable=self.input)
        self.input_entry.grid(row=3, column=1, sticky=tk.EW, pady=10)

        footframe = ttk.Frame(self)
        footframe.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NSEW)
        footframe.grid_columnconfigure(0, weight=1)

        self.response_label = ttk.Label(footframe, textvariable=self.response, width=16)
        self.response_label.grid(row=0, column=0, sticky=tk.EW, padx=5)

        ttk.Button(footframe, textvariable=self.button_label, command=self.button_press, width=8).grid(row=0, column=1, sticky=tk.E, padx=5)

        self.input.trace_add("write", self.input_write)
        self.bind("<Return>", self.button_press)

        self.new_game()

    def new_game(self):
        self.points.set(0)
        self.lives.set(3)
        self.game.reset()
        self.render_question()

    def button_press(self, *args):
        if self.current_question:
            if input := self.input.get():
                ok, correct_verbs = self.game.submit_answer(self.current_question, input)
                self.render_response(ok, correct_verbs)

                if ok:
                    self.points.set(self.points.get() + 1)
                else:
                    self.lives.set(self.lives.get() - 1)

                self.current_question = None
        elif self.lives.get() == 0:
            self.game_over(self.points.get())
        else:
            self.render_question()

    def input_write(self, name: str, index: str, mode: str) -> None:
        # make it easy to write umlauts on a US keyboard
        def get_umlaut(s: str) -> str | None:
            match s:
                case '"a':  return 'ä'
                case '"e':  return 'ë'
                case '"o':  return 'ö'
                case '"u':  return 'ü'
                case _:     return None

        text = self.input.get()
        i = 0
        while i < len(text) - 1:
            if (umlaut := get_umlaut(text[i:i+2])):
                text = text[:i] + umlaut + text[i+2:]
            i += 1
        self.input.set(text)

    def render_question(self) -> None:
        q = self.game.get_next_question()
        self.current_question = q.verbform
        self.verb.set(q.verbform.infinitiv)
        self.verbform.set(q.verbform.form)
        self.translation.set(q.english)
        self.question.set(q.example.removesuffix(' …'))
        self.input.set("")
        self.input_entry.config(state='enabled')
        self.input_entry.focus()
        self.response.set("")
        self.button_label.set("Eingabe")

    def render_response(self, ok: bool, correct_verbs: set[str]) -> None:
        if ok:
            self.response.set("Richtig!")
            self.response_label.config(foreground='green')
        else:
            self.response.set(f"Falsch! {'/'.join(correct_verbs)}")
            self.response_label.config(foreground='red')

        self.button_label.set("Nächste")
        self.input_entry.config(state='disabled')

    def game_over(self, score: int) -> None:
        d = GameOverDialog(score, self)
        if d.result:
            self.highscores.update(d.result, score)
            HighScoreDialog(self.highscores.format(), self)
        resp = messagebox.askquestion(title = 'Spiel Aus!', message="Noch ein Spiel?")
        if resp == 'yes':
            self.new_game()
        else:
            self.destroy()


if __name__ == "__main__":
    Application().mainloop()
