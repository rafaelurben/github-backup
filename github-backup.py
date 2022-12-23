# Create a backup of all GitHub repositories (includes personal, if authenticated)
# This requires GitHub CLI to be installed and configured (https://cli.github.com/)

import os.path
from pathlib import Path
import subprocess
import sys
import json

print("[GitHub Backup] Checking if GitHub CLI is installed...")

p1 = subprocess.Popen(['gh', '--version'], stdout=subprocess.PIPE)
t1 = p1.stdout.read().decode('utf-8', errors='replace').strip()
if "gh version" not in t1:
    print("[GitHub Backup] GitHub CLI is not installed. Please install it from https://cli.github.com/")
    sys.exit()
else:
    print("[GitHub Backup] GitHub CLI is installed. Continuing...")

print("[GitHub Backup] Checking if GitHub CLI is authenticated...")

try:
    p2 = subprocess.Popen(['gh', 'api', 'user'], stdout=subprocess.PIPE)
    t2 = p2.stdout.read().decode('utf-8', errors='replace').strip()
    j2 = json.loads(t2)
    username = j2['login']
    print(f"[GitHub Backup] GitHub CLI is authenticated as {username}. Continuing...")
except json.JSONDecodeError as e:
    print("[GitHub Backup] GitHub CLI is not authenticated! Run 'gh auth login' and login!")
    sys.exit()

username = input(f"[GitHub Backup] Username (leave empty for {username}): ") or username

p3 = subprocess.Popen(['gh', 'repo', 'list', '-L', '10000000', '--json', 'name,owner,nameWithOwner,url', username], stdout=subprocess.PIPE)
t3 = p3.stdout.read().decode('utf-8', errors='ignore').strip()
j = json.loads(t3)

repocount = len(j)
print(f"[GitHub Backup] Found {repocount} repositories for user {username}.")

backupdir = input("[GitHub Backup] Backup directory: ")
backupdir = Path(os.path.abspath(backupdir))

try:
    os.chdir(backupdir)
except FileNotFoundError:
    print("[GitHub Backup] Backup directory does not exist. Creating...")
    os.mkdir(backupdir)
    os.chdir(backupdir)
print(f"[GitHub Backup] Backup directory set to '{backupdir}'.")

input("[GitHub Backup] Ready! Press enter to start or press Ctrl+C to cancel.")

for i, repo in enumerate(j):
    name = repo['nameWithOwner']
    url = repo['url']
    repodir = backupdir / repo['owner']['login'] / repo['name']

    print(f"[GitHub Backup] ({i+1}/{repocount}) Backing up {name} ({url})...")

    p4 = subprocess.call(['gh', 'repo', 'clone', url, repodir, '--', '--depth', '1'], cwd=backupdir)

    subprocess.call("rmdir /S /Q .git", shell=True, cwd=repodir)

    print(f"[GitHub Backup] ({i+1}/{repocount}) Backed up {name}.")

print("[GitHub Backup] Done!")
