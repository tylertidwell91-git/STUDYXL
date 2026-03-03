import random
import re
from pathlib import Path


MARKDOWN_PATH = Path.home() / "Citation_XL_XLS_Chapter2_5_QA.md"


class Question:
    def __init__(self, chapter: str, number: str, prompt: str, options, answer_line: str, explanation: str):
        self.chapter = chapter
        self.number = number
        self.prompt = prompt
        self.options = options
        self.answer_line = answer_line
        self.explanation = explanation.strip()

    @property
    def full_question_text(self) -> str:
        header = f"{self.chapter} – Question {self.number}"
        opts = "\n".join(self.options)
        return f"{header}\n\n{self.prompt}\n\n{opts}"

    @property
    def full_answer_text(self) -> str:
        parts = [self.answer_line]
        if self.explanation:
            parts.append("")
            parts.append(self.explanation)
        return "\n".join(parts)


def parse_markdown_questions(text: str):
    lines = text.splitlines()
    questions = []

    current_chapter = ""
    i = 0
    q_num_pattern = re.compile(r"^### Question (\d+)")

    while i < len(lines):
        line = lines[i]

        if line.startswith("Chapter ") and "–" in line:
            current_chapter = line.strip()
            i += 1
            continue

        m = q_num_pattern.match(line.strip())
        if m:
            number = m.group(1)
            i += 1

            # Expect bold question line
            while i < len(lines) and not lines[i].strip().startswith("**"):
                i += 1
            if i >= len(lines):
                break
            prompt_line = lines[i].strip()
            prompt = prompt_line.strip("* ").strip()
            i += 1

            # Collect options until we hit "Correct answer"
            options = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("**Correct answer:"):
                    break
                if re.match(r"^[A-D]\.\s", s):
                    options.append(s)
                i += 1

            # Answer line
            if i >= len(lines):
                break
            answer_line = lines[i].strip().strip("* ")
            i += 1

            # Explanation until next '---' or '### Question' or 'Chapter'
            explanation_lines = []
            while i < len(lines):
                s = lines[i]
                if s.strip() == "---":
                    i += 1
                    break
                if q_num_pattern.match(s.strip()):
                    break
                if s.startswith("Chapter ") and "–" in s:
                    break
                explanation_lines.append(s)
                i += 1

            explanation = "\n".join(explanation_lines)
            questions.append(
                Question(
                    chapter=current_chapter,
                    number=number,
                    prompt=prompt,
                    options=options,
                    answer_line=answer_line,
                    explanation=explanation,
                )
            )
        else:
            i += 1

    return questions


def main():
    if not MARKDOWN_PATH.exists():
        raise SystemExit(f"Markdown file not found: {MARKDOWN_PATH}")

    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    questions = parse_markdown_questions(text)
    if not questions:
        raise SystemExit("No questions parsed from markdown file.")

    print(f"Loaded {len(questions)} questions.")
    print("Press Ctrl+C at any time to quit.\n")

    while True:
        q = random.choice(questions)
        print("=" * 80)
        print(q.full_question_text)
        print("=" * 80)
        user = input("Press Enter to show answer (or type 'q' then Enter to quit): ").strip().lower()
        if user == "q":
            break
        print("\nANSWER:\n")
        print(q.full_answer_text)
        print("-" * 80)
        again = input("Press Enter for next question (or type 'q' then Enter to quit): ").strip().lower()
        if again == "q":
            break
        print()


if __name__ == "__main__":
    main()


