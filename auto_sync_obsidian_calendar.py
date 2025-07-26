import os
import re
import subprocess
import uuid
from datetime import datetime, time

# === PATHS ===
VAULT_PATH = r"C:\Users\Kenth\Obsidian Vault\Knowledge Base"
REPO_PATH = r"C:\Users\Kenth\obsidian-spaced-repetition-calendar"
OUTPUT_FILE = os.path.join(REPO_PATH, "SpacedRepetition.ics")
GIT_COMMIT_MSG = "🔄 Auto-update spaced repetition calendar"

# === GITHUB AUTH ===
GITHUB_USERNAME = "kenth619"
GITHUB_EMAIL = "kenth_619@hotmail.com"
GITHUB_PAT = os.getenv("GITHUB_PAT")
REMOTE_NAME = "origin"
SECURE_URL = f"https://{GITHUB_USERNAME}:{GITHUB_PAT}@github.com/{GITHUB_USERNAME}/obsidian-spaced-repetition-calendar.git"
SAFE_URL = f"https://github.com/{GITHUB_USERNAME}/obsidian-spaced-repetition-calendar.git"

# === CALENDAR SETTINGS ===
YAML_SR_DUE_REGEX = r'^sr-due:\s*(\d{4}-\d{2}-\d{2})$'
TIMEZONE_ID = "America/Puerto_Rico"
EVENT_TIME = time(hour=16, minute=30)  # 4:30 PM local

events = []
file_count = 0
total_matches = 0

print(f"\n📁 Scanning folder: {VAULT_PATH}\n")

# === SCAN VAULT AND CREATE EVENTS ===
for root, _, files in os.walk(VAULT_PATH):
    for file in files:
        if file.endswith(".md"):
            file_count += 1
            full_path = os.path.join(root, file)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                frontmatter = re.findall(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
                if frontmatter:
                    lines = frontmatter[0].splitlines()
                    for line in lines:
                        match = re.match(YAML_SR_DUE_REGEX, line.strip())
                        if match:
                            sr_due_date = match.group(1)
                            due_date = datetime.strptime(sr_due_date, "%Y-%m-%d").date()
                            start_dt = datetime.combine(due_date, EVENT_TIME)
                            end_dt = datetime.combine(due_date, time(hour=17, minute=30))  # 5:30 PM
                            uid = f"{uuid.uuid4()}@obsidian"

                            print(f"📄 {file} — 📅 Due: {sr_due_date}")

                            vevent = f"""BEGIN:VEVENT
UID:{uid}
SUMMARY:📚 Obsidian Review
DESCRIPTION:Review cards from {file}
DTSTART;TZID={TIMEZONE_ID}:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND;TZID={TIMEZONE_ID}:{end_dt.strftime('%Y%m%dT%H%M%S')}
END:VEVENT"""
                            events.append(vevent)
                            total_matches += 1

# === BUILD CALENDAR CONTENT ===
calendar_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Obsidian Spaced Repetition//EN
CALSCALE:GREGORIAN

BEGIN:VTIMEZONE
TZID:{TIMEZONE_ID}
BEGIN:STANDARD
DTSTART:19710101T000000
TZOFFSETFROM:-0400
TZOFFSETTO:-0400
TZNAME:AST
END:STANDARD
END:VTIMEZONE
"""

calendar_content += "\n\n".join(events)
calendar_content += "\n\nEND:VCALENDAR"

# === WRITE ICS FILE ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(calendar_content)

# === PUSH TO GITHUB SAFELY ===
def push_to_github():
    # Ensure commit identity
    subprocess.run(["git", "config", "user.name", GITHUB_USERNAME], cwd=REPO_PATH)
    subprocess.run(["git", "config", "user.email", GITHUB_EMAIL], cwd=REPO_PATH)

    # Use secure URL with PAT for this operation
    subprocess.run(["git", "remote", "set-url", REMOTE_NAME, SECURE_URL], cwd=REPO_PATH)

    # Stage and commit first to avoid "unstaged changes" error
    subprocess.run(["git", "add", "SpacedRepetition.ics"], cwd=REPO_PATH)
    subprocess.run(["git", "commit", "-m", GIT_COMMIT_MSG], cwd=REPO_PATH)

    # Pull remote changes with rebase to keep history clean
    subprocess.run(["git", "pull", "--rebase"], cwd=REPO_PATH)

    # Push updates
    subprocess.run(["git", "push", REMOTE_NAME, "main"], cwd=REPO_PATH)

    # Revert to safe URL without token
    subprocess.run(["git", "remote", "set-url", REMOTE_NAME, SAFE_URL], cwd=REPO_PATH)

push_to_github()

# === SUMMARY ===
print(f"\n✅ Scan complete! {file_count} files searched.")
print(f"📌 {total_matches} review entries added to calendar.")
print(f"🌐 View at: https://kenth619.github.io/obsidian-spaced-repetition-calendar/SpacedRepetition.ics")
