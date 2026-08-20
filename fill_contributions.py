"""
Contribution History Generator.
Generates historical commits with past timestamps to populate
and customize your native GitHub profile contribution grid (green squares).

Usage:
    python fill_contributions.py --days 365 --max-commits 5
"""

import argparse
import datetime
import random
import subprocess
import os

LOG_FILE = "LOG.md"

def create_commit(date_str: str, index: int):
    # Ensure LOG.md exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📅 Daily Activity & Contribution Log\n\n")

    # Append a line
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"- **{date_str}** — Activity contribution update #{index}\n")

    # Format date string for GIT_AUTHOR_DATE and GIT_COMMITTER_DATE
    iso_date = f"{date_str}T12:{random.randint(10,59):02d}:{random.randint(10,59):02d}"
    
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = iso_date
    env["GIT_COMMITTER_DATE"] = iso_date

    subprocess.run(["git", "add", LOG_FILE], check=True, env=env)
    subprocess.run(["git", "commit", "-m", f"Contribution update for {date_str}"], check=True, env=env)

def main():
    parser = argparse.ArgumentParser(description="Generate historical contributions for GitHub graph")
    parser.add_argument("--days", type=int, default=30, help="Number of past days to generate commits for")
    parser.add_argument("--max-commits", type=int, default=3, help="Max commits per day")
    args = parser.parse_args()

    today = datetime.date.today()
    print(f"Generating contributions for past {args.days} days...")

    for day_offset in range(args.days, 0, -1):
        target_date = today - datetime.timedelta(days=day_offset)
        date_str = target_date.isoformat()

        # Randomize whether this day gets commits (e.g. 70% chance)
        if random.random() < 0.70:
            commit_count = random.randint(1, args.max-commits)
            for i in range(1, commit_count + 1):
                create_commit(date_str, i)
            print(f"[{date_str}] Created {commit_count} commit(s)")

    print("\n✅ Historical commits generated successfully!")
    print("Run 'git push origin main' to push your updated contribution history to GitHub.")

if __name__ == "__main__":
    main()
