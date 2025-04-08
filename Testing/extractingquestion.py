import re

def extract_questions_from_text(text):
    # Remove known headers and metadata patterns
    text = re.sub(r"GOVERNMENT POLYTECHNIC.*?Instruction :-", "", text, flags=re.DOTALL)
    text = re.sub(r"EXAMSEATNO.*?DATE.*?\n", "", text)
    text = re.sub(r"Q\d+\]?\s*\|?\s*Attempt.*?\n", "", text)
    text = re.sub(r"--- Page \d+ ---", "", text)

    # Normalize lines
    text = text.replace('—', '-').replace('=', '-').replace('|', '')
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Regular expression for identifying question lines
    question_patterns = [
        r"^(?:[a-z]\)|[a-z]\.)\s",                  # a) or a. type
        r"^(?:[ivxlcdm]+\))\s",                    # Roman numeral like i), ii)
        r"^Q\d+\.\s",                              # Q1. Q2. Q3. pattern
        r"^(?:[0-9]+\))\s",                        # 1), 2) numbered points
        r"^(Define|Explain|Distinguish|Draw|Compare|List|State|Write|Find|Consider|Determine)\b",
    ]

    question_regex = re.compile("|".join(question_patterns), re.IGNORECASE)

    # Extract matching lines
    questions = []
    buffer = ""

    for line in lines:
        if question_regex.match(line):
            if buffer:
                questions.append(buffer.strip())
                buffer = ""
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        questions.append(buffer.strip())

    return questions


# ---- Example usage ----
with open("extracted_text.txt", "r", encoding="utf-8") as file:
    text = file.read()

questions = extract_questions_from_text(text)

# Print extracted questions
for i, q in enumerate(questions, start=1):
    print(f"{i}. {q}")
