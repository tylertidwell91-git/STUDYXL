import random
import re
from pathlib import Path


# Markdown lives alongside this script in the project directory
MARKDOWN_PATH = (Path(__file__).resolve().parent / "Citation_XL_XLS_Chapter2_5_QA.md").resolve()


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
    step_num_pattern = re.compile(r"^### Step (\d+)")
    # Memory Items: ## APU FIRE, ## BATT O'TEMP, etc. (not "Chapter X –" or "Required Knowledge")
    memory_procedure_pattern = re.compile(r"^##\s+(.+)$")

    while i < len(lines):
        line = lines[i]

        # Chapter-style headings
        if line.startswith("Chapter ") and "–" in line:
            current_chapter = line.strip()
            i += 1
            continue
        # Non-chapter category heading (e.g., Required Knowledge, Limitations)
        if line.strip().startswith("Required Knowledge"):
            current_chapter = "Required Knowledge"
            i += 1
            continue
        if line.strip().startswith("Limitations"):
            current_chapter = "Limitations"
            i += 1
            continue
        # Memory Items procedure (e.g. ## APU FIRE) — level-2 heading that starts a procedure block
        mem_proc = memory_procedure_pattern.match(line.strip()) if line.strip().startswith("## ") else None
        if mem_proc:
            proc_name = mem_proc.group(1).strip()
            # Skip the section title "Memory Items (CE-560XL G5000)" and similar
            if proc_name and not proc_name.lower().startswith("memory items"):
                current_chapter = "Memory Items – " + proc_name
            i += 1
            continue

        # Memory Items: ### Step N with optional A.–D. options and **Correct answer:** or **Answer:**
        step_m = step_num_pattern.match(line.strip())
        if step_m and current_chapter.startswith("Memory Items"):
            number = step_m.group(1)
            i += 1
            # Optional blank; then bold question line
            while i < len(lines) and not lines[i].strip().startswith("**"):
                i += 1
            if i >= len(lines):
                break
            prompt_line = lines[i].strip()
            prompt = prompt_line.strip("* ").strip()
            i += 1
            # Collect optional A.–D. options
            options = []
            while i < len(lines):
                s = lines[i].strip()
                if re.match(r"^[A-D]\.\s", s):
                    options.append(s)
                    i += 1
                    continue
                if s.startswith("**Correct answer:") or s.startswith("**Answer:"):
                    break
                i += 1
            # Answer line: **Correct answer: X – ...** or **Answer: ...**
            answer_line = ""
            if i < len(lines):
                s = lines[i].strip()
                if s.startswith("**Correct answer:"):
                    answer_line = s.replace("**Correct answer:", "").strip().strip("* ").strip()
                    i += 1
                elif s.startswith("**Answer:"):
                    answer_line = s.replace("**Answer:", "").strip().strip("* ").strip()
                    i += 1
            # Explanation until next '---' or '### Step' or '## '
            explanation_lines = []
            while i < len(lines):
                s = lines[i]
                if s.strip() == "---":
                    i += 1
                    break
                if step_num_pattern.match(s.strip()):
                    break
                if s.strip().startswith("## "):
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


