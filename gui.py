import tkinter as tk
from tkinter import ttk

from VerbMeister_Blitz import Game

class Application(ttk.Frame):
    def __init__(self, root: tk.Tk):
        super().__init__(root, padding="3 3 12 12")

        self.game = Game()

        root.title("VerbMeister")

        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.verb = tk.StringVar()
        self.question = tk.StringVar()
        self.input = tk.StringVar()
        self.response = tk.StringVar()
        self.points = tk.IntVar(value=0)
        self.lives = tk.IntVar(value=3)

        ttk.Label(self, textvariable=self.points, foreground='blue').grid(row=1, column=1, sticky=tk.NW)
        ttk.Label(self, textvariable=self.verb).grid(row=1, column=2)
        ttk.Label(self, textvariable=self.lives, foreground='red').grid(row=1, column=3, sticky=tk.NE)

        ttk.Label(self, textvariable=self.question).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))

        input_entry = ttk.Entry(self, width=7, textvariable=self.input)
        input_entry.grid(row=2, column=3, sticky=(tk.W, tk.E))

        self.response_label = ttk.Label(self, textvariable=self.response)
        self.response_label.grid(row=3, column=1, columnspan=2)

        self.button = ttk.Button(self, text="Check", command=self.button_press)
        self.button.grid(row=3, column=3, sticky=tk.W)

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        input_entry.focus()
        root.bind("<Return>", self.button_press)

        self.render_question()

    def button_press(self, *args):
        if self.current_question:
            ok, correct_verbs = self.game.submit_answer(self.current_question, self.input.get())
            if ok:
                self.points.set(self.points.get() + 1)
                self.response.set("Richtig!")
                self.response_label.config(foreground='green')
            else:
                self.lives.set(self.lives.get() - 1)
                self.response.set(f"Falsch! {'/'.join(correct_verbs)}")
                self.response_label.config(foreground='red')

            self.current_question = None
            self.button.config(text="Next")
        else:
            self.render_question()

    def render_question(self):
        self.current_question = self.game.get_next_question()
        self.verb.set(self.current_question.infinitiv)
        self.question.set(self.current_question.form)
        self.input.set("")
        self.response.set("")
        self.button.config(text="Check")

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
