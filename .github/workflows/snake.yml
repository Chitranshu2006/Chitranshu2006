"""
Daily log updater.
Appends a timestamped entry to LOG.md so each scheduled commit
has real, meaningful content instead of being an empty filler commit.

Customize the `generate_entry()` function to log whatever is
actually useful to you: a quote, a stat, a task note, etc.
"""

import datetime
import os

LOG_FILE = "LOG.md"


def generate_entry() -> str:
    today = datetime.date.today().isoformat()
    # Customize this: e.g. pull today's LeetCode problem solved,
    # a git commit count from your other repos, a "what I learned today" note, etc.
    return f"- **{today}** — logged automatically.\n"


def main():
    entry = generate_entry()

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("# Daily Log\n\n")

    with open(LOG_FILE, "a") as f:
        f.write(entry)

    print(f"Appended entry: {entry.strip()}")


if __name__ == "__main__":
    main()
