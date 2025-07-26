import os
import re
import subprocess
from datetime import datetime
from ics import Calendar, Event

VAULT_PATH = r"C:\Users\Kenth\Obsidian Vault\Knowledge Base"
REPO_PATH = r"C:\Users\Kenth\obsidian-spaced-repetition-calendar"
OUTPUT_FILE = os.path.join(REPO_PATH, "SpacedRepetition.ics")
GIT_COMMIT_MSG = "🔄 Auto-update spaced repetition calendar"

calendar = Calendar()
file_count = 0
total_matches = 0

# New regex to match sr-due in YAML frontmatter
YAML_SR_DUE_REGEX = r'^sr-due:\s*(\d{4}-\d{2}-\d{2})$'

print(f"\n📁 Scanning folder: {VAULT_PATH}\n")

for root, _, files in os.walk(VAULT_PATH):
    for file in files:
        if file.endswith(".md"):
            file_count += 1
            full_path = os.path.join(root, file)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Look inside frontmatter block only
                frontmatter = re.findall(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
                if frontmatter:
                    lines = frontmatter[0].splitlines()
                    for line in lines:
                        match = re.match(YAML_SR_DUE_REGEX, line.strip())
                        if match:
                            sr_due_date = match.group(1)
                            print(f"📄 {file} — 📅 Due: {sr_due_date}")
                            due_date = datetime.strptime(sr_due_date, "%Y-%m-%d")
                            event = Event()
                            event.name = "📚 Obsidian Review"
                            event.begin = due_date.strftime("%Y-%m-%dT09:00:00")
                            event.duration = {"minutes": 30}
                            event.description = f"Review cards from {file}"
                            calendar.events.add(event)
                            total_matches += 1

# Write ICS
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(calendar)

# GitHub push
def push_to_github():
    subprocess.run(["git", "add", "SpacedRepetition.ics"], cwd=REPO_PATH)
    subprocess.run(["git", "commit", "-m", GIT_COMMIT_MSG], cwd=REPO_PATH)
    subprocess.run(["git", "push"], cwd=REPO_PATH)

push_to_github()

# Summary
print(f"\n✅ Scan complete! {file_count} files searched.")
print(f"📌 {total_matches} review entries added to calendar.")
print(f"🌐 View at: https://kenth619.github.io/obsidian-spaced-repetition-calendar/SpacedRepetition.ics")
