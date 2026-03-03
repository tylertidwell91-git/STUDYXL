import tkinter as tk
from xl_xls_flashcards import MARKDOWN_PATH, parse_markdown_questions
import random


class FlashcardGUI(tk.Tk):
    def __init__(self, questions):
        super().__init__()
        self.title("Citation XL/XLS Study Cards")
        self.geometry("900x600")
        self.minsize(700, 400)

        self.questions = questions
        self.current = None

        # Question area (bright background so it's clearly visible)
        self.question_label = tk.Label(
            self,
            text="If you see this text, the question area is working.",
            anchor="nw",
            justify="left",
            padx=10,
            pady=10,
            bg="yellow",
        )

        # Answer area
        self.answer_label = tk.Label(
            self,
            text="",
            anchor="nw",
            justify="left",
            padx=10,
            pady=10,
            fg="darkgreen",
            bg="lightgreen",
        )

        # Buttons
        self.show_button = tk.Button(self, text="Show Answer", command=self.show_answer)
        self.next_button = tk.Button(self, text="Next Question", command=self.next_question)
        self.quit_button = tk.Button(self, text="Quit", command=self.destroy)

        # Layout
        self.question_label.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 5))
        self.answer_label.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", pady=(0, 10))
        self.show_button.pack(in_=button_frame, side="left", padx=5)
        self.next_button.pack(in_=button_frame, side="left", padx=5)
        self.quit_button.pack(in_=button_frame, side="left", padx=5)

        # After layout, show initial message
        self.set_question_text(f"Loaded {len(self.questions)} questions.\nClick 'Next Question' to begin.")
        self.set_answer_text("")

    def set_question_text(self, text: str) -> None:
        self.question_label.configure(text=text)

    def set_answer_text(self, text: str) -> None:
        self.answer_label.configure(text=text)

    def next_question(self) -> None:
        self.current = random.choice(self.questions)
        self.set_question_text(self.current.full_question_text)
        self.set_answer_text("")

    def show_answer(self) -> None:
        if self.current is not None:
            self.set_answer_text(self.current.full_answer_text)


def main():
    if not MARKDOWN_PATH.exists():
        raise SystemExit(f"Markdown file not found: {MARKDOWN_PATH}")

    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    questions = parse_markdown_questions(text)
    if not questions:
        raise SystemExit("No questions parsed from markdown file.")

    app = FlashcardGUI(questions)
    app.mainloop()


if __name__ == "__main__":
    main()

