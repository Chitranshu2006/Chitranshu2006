"""
Daily log updater.
Appends timestamped entries to LOG.md on each run.
Each scheduled run creates a unique commit for contribution tracking.
"""

import datetime
import os
import random

LOG_FILE = "LOG.md"

QUOTES = [
    "Code is like humor. When you have to explain it, it's bad.",
    "First, solve the problem. Then, write the code.",
    "Experience is the name everyone gives to their mistakes.",
    "Make it work, make it right, make it fast.",
    "Simplicity is prerequisite for reliability.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "Knowledge is power.",
    "Fix the cause, not just the symptom.",
    "Optimism is an occupational hazard of programming: feedback is the treatment.",
    "In order to be irreplaceable, one must always be different.",
    "Programming is the art of telling another human what one wants the computer to do.",
    "The best error message is the one that never shows up.",
    "Code never lies, comments sometimes do.",
    "The most disastrous thing that you can ever learn is your first programming language.",
    "Software is a great combination of artistry and engineering.",
]


def generate_entry() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
    quote = random.choice(QUOTES)
    return f"- **{timestamp}** — {quote}\n"


def main():
    # Create file with header if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📅 Daily Activity & Contribution Log\n\n")

    # Append new entry — no duplicate check so each run creates a unique commit
    entry = generate_entry()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"Appended: {entry.strip()}")


if __name__ == "__main__":
    main()
