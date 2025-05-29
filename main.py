#!/usr/bin/env python3
"""
daily_commits.py  –  Append to a file and create 1-10 random commits dated within today.

Usage
-----
    python daily_commits.py [path/to/file] [min_commits max_commits]

Defaults
--------
    path/to/file      activity.txt           (relative to repo root)
    min_commits       1
    max_commits       10

Environment variables
---------------------
    PUSH_AFTER_RUN    1  (set to 0/false to skip `git push`)
"""

import datetime as dt
import os
import pathlib
import random
import subprocess
import sys


def rand_time_today() -> dt.datetime:
    """Return a random time today (local time)."""
    now = dt.datetime.now()
    return now.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0,
    )


def main() -> None:
    # ---------- Parse CLI ----------------------------------------------------
    target_file = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("activity.txt")
    min_c = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    max_c = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    if min_c > max_c:
        min_c, max_c = max_c, min_c
    n_commits = random.randint(min_c, max_c)

    # ---------- Make sure we’re inside a Git repo ---------------------------
    repo_root = (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    )
    os.chdir(repo_root)

    # ---------- Loop & commit ------------------------------------------------
    for i in range(1, n_commits + 1):
        # 1. Touch / append to the file so every commit has real content
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open("a") as f:
            f.write(f"{dt.datetime.now().isoformat()}  –  automated commit {i}/{n_commits}\n")

        # 2. Stage changes
        subprocess.run(["git", "add", str(target_file)], check=True)

        # 3. Prepare faux time & environment
        fake_time = rand_time_today().isoformat()
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = fake_time
        env["GIT_COMMITTER_DATE"] = fake_time

        # 4. Commit
        msg = f"Automated commit on {dt.date.today()}  ({i}/{n_commits})"
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True)
        print(f"✓ commit {i}/{n_commits} at {fake_time}")

    # ---------- Push (once) --------------------------------------------------
    if os.getenv("PUSH_AFTER_RUN", "1").lower() not in {"0", "false"}:
        subprocess.run(["git", "push"], check=True)
        print("✓ pushed to remote")


if __name__ == "__main__":
    main()

