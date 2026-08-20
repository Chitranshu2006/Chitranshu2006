"""
Daily log updater.
Appends a timestamped entry to LOG.md so each scheduled commit
has real, meaningful content. Prevents duplicate entries for the same day.
"""

import datetime
import os
import random

LOG_FILE = "LOG.md"

QUOTES = [
    "Code is like humor. When you have to explain it, it’s bad.",
    "First, solve the problem. Then, write the code.",
    "Experience is the name everyone gives to their mistakes.",
    "Make it work, make it right, make it fast.",
    "Simplicity is prerequisite for reliability.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "Knowledge is power.",
    "Fix the cause, not just the symptom.",
    "Optimism is an occupational hazard of programming: feedback is the treatment.",
    "In order to be irreplaceable, one must always be different.",
]


def generate_entry() -> str:
    today = datetime.date.today().isoformat()
    quote = random.choice(QUOTES)
    return f"- **{today}** — {quote}\n"


def main():
    today = datetime.date.today().isoformat()
    
    # Create file with header if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📅 Daily Activity & Contribution Log\n\n")

    # Read existing entries to check for duplicates
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # If today is already logged, don't add duplicate
    if f"**{today}**" in content:
        print(f"Entry for {today} already exists. Skipping duplicate generation.")
        return

    # Append new entry
    entry = generate_entry()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"Appended entry: {entry.strip()}")


if __name__ == "__main__":
    main()
