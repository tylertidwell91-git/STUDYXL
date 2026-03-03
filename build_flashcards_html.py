import json
from pathlib import Path

from xl_xls_flashcards import MARKDOWN_PATH, parse_markdown_questions


HTML_PATH = Path.home() / "Citation_XL_XLS_Flashcards.html"


def build_questions_data():
    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    parsed = parse_markdown_questions(text)
    data = []
    for q in parsed:
        # Extract answer text without the "Correct answer:" prefix if present
        answer = q.answer_line
        prefix = "Correct answer:"
        if answer.startswith(prefix):
            answer = answer[len(prefix) :].strip()

        # Try to convert question number to int when possible
        try:
            number = int(q.number)
        except ValueError:
            number = q.number

        data.append(
            {
                "chapter": q.chapter,
                "number": number,
                "prompt": q.prompt,
                "options": q.options,
                "answer": answer,
                "explanation": q.explanation.strip(),
            }
        )
    return data


def update_html(questions_data):
    if not HTML_PATH.exists():
        raise SystemExit(f"HTML file not found: {HTML_PATH}")

    html = HTML_PATH.read_text(encoding="utf-8")

    marker = "const questions ="
    start = html.find(marker)
    if start == -1:
        raise SystemExit("Could not find 'const questions =' in HTML file.")

    # Find the end of the existing questions array: first occurrence of '];' after the marker
    end = html.find("];", start)
    if end == -1:
        raise SystemExit("Could not find end of questions array (' ];') in HTML file.")
    end += 2  # include the closing bracket and semicolon

    new_array = "const questions = " + json.dumps(questions_data, indent=2, ensure_ascii=False) + ";"

    updated = html[:start] + new_array + html[end:]
    HTML_PATH.write_text(updated, encoding="utf-8")


def main():
    if not MARKDOWN_PATH.exists():
        raise SystemExit(f"Markdown file not found: {MARKDOWN_PATH}")

    questions_data = build_questions_data()
    if not questions_data:
        raise SystemExit("No questions parsed from markdown file.")

    update_html(questions_data)
    print(f"Updated {HTML_PATH.name} with {len(questions_data)} questions from {MARKDOWN_PATH.name}.")


if __name__ == "__main__":
    main()

