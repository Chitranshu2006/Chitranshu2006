"""
Contribution History Generator.
Generates historical commits with past timestamps to populate
and customize your native GitHub profile contribution grid (green squares).

Usage:
    python fill_contributions.py --days 365 --max-commits 200

WARNING: Running with default settings creates ~200 commits per day.
         For 365 days, that's ~73,000 commits. This will take a while.
         Make sure you're ready before running!
"""

import argparse
import datetime
import random
import subprocess
import os

LOG_FILE = "LOG.md"

MESSAGES = [
    "chore: update activity log",
    "feat: daily contribution update",
    "docs: update project documentation",
    "refactor: improve code structure",
    "style: format code",
    "fix: resolve minor issues",
    "build: update dependencies",
    "perf: optimize performance",
    "test: add test coverage",
    "ci: update workflow configuration",
]


def create_commit(date_str: str, index: int):
    # Ensure LOG.md exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 📅 Daily Activity & Contribution Log\n\n")

    # Append a line
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"- **{date_str}** — Activity #{index}\n")

    # Randomize the time so commits look natural
    hour = random.randint(6, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    iso_date = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}"

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = iso_date
    env["GIT_COMMITTER_DATE"] = iso_date

    msg = random.choice(MESSAGES)
    subprocess.run(["git", "add", LOG_FILE], check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", f"{msg} ({date_str} #{index})"],
                   check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(
        description="Generate historical contributions for GitHub graph"
    )
    parser.add_argument("--days", type=int, default=365,
                        help="Number of past days to generate commits for (default: 365)")
    parser.add_argument("--min-commits", type=int, default=180,
                        help="Minimum commits per day (default: 180)")
    parser.add_argument("--max-commits", type=int, default=220,
                        help="Maximum commits per day (default: 220)")
    args = parser.parse_args()

    today = datetime.date.today()
    total_commits = 0
    avg = (args.min_commits + args.max_commits) // 2

    print(f"🚀 Generating {args.min_commits}-{args.max_commits} commits/day "
          f"for the past {args.days} days...")
    print(f"   Estimated total: ~{avg * args.days:,} commits")
    print()

    for day_offset in range(args.days, 0, -1):
        target_date = today - datetime.timedelta(days=day_offset)
        date_str = target_date.isoformat()
        commit_count = random.randint(args.min_commits, args.max_commits)

        for i in range(1, commit_count + 1):
            create_commit(date_str, i)

        total_commits += commit_count
        print(f"  [{date_str}] ✓ {commit_count} commits  (total: {total_commits:,})")

    print(f"\n✅ Generated {total_commits:,} historical commits!")
    print("Run 'git push origin main' to push to GitHub.")


if __name__ == "__main__":
    main()
