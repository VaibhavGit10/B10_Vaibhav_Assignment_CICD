#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime

LOG_FILE = "CICD_EC2_PYTHON_LOGS"

# Redirect output to log file
sys.stdout = open(LOG_FILE, "a")
sys.stderr = sys.stdout

print("\n-------------------------------")
print(f"📅 Trigger Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-------------------------------")

# Install PyGithub if not available
try:
    from github import Github
except ImportError:
    print("📦 PyGithub not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyGithub"])
    from github import Github
    print("✅ PyGithub installed.")

# Load environment variables from a .env file manually
def load_env_file(filename):
    if not os.path.exists(filename):
        print(f"❌ Environment file {filename} not found.")
        sys.exit(1)
    with open(filename) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

load_env_file("secret_key.env")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REPO_NAME = os.getenv("REPOSITORY_NAME")

if not ACCESS_TOKEN or not REPO_NAME:
    print("❌ ACCESS_TOKEN or REPOSITORY_NAME missing in secret_key.env.")
    sys.exit(1)

# Connect to GitHub
try:
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(REPO_NAME)
    print(f"✅ Connected to GitHub Repo: {REPO_NAME}")
except Exception as e:
    print(f"❌ Error connecting to GitHub: {e}")
    sys.exit(1)

# Fetch latest 5 commits
try:
    commits = repo.get_commits()
    latest_commit_shas = [commit.sha[:7] for commit in commits[:5]]
except Exception as e:
    print(f"❌ Failed to fetch commits: {e}")
    sys.exit(1)

commit_file = "existing_commits.txt"

# Reusable function to trigger deployment
def trigger_deployment():
    print("🚀 Starting deployment script...")
    try:
        process = subprocess.Popen(["/bin/bash", "/home/ubuntu/CICD_EC2_DEPLOY.sh"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        print("✅ Deployment script finished.")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

# First time setup
if not os.path.exists(commit_file):
    with open(commit_file, "w") as f:
        for sha in latest_commit_shas:
            f.write(sha + "\n")
    print("🆕 First run. Commit list saved.")
    trigger_deployment()
else:
    with open(commit_file, "r") as f:
        existing_commits = set(line.strip() for line in f)

    new_commits = [sha for sha in latest_commit_shas if sha not in existing_commits]

    if new_commits:
        print("   New commits detected.")
        with open(commit_file, "w") as f:
            for sha in latest_commit_shas:
                f.write(sha + "\n")
        trigger_deployment()
    else:
        print("✅ No new commits found. Deployment skipped.")

# Show commit details
print("\n🔍 Recent Commits:")
for commit in commits[:5]:
    print(f"- Short SHA: {commit.sha[:7]}")
    print(f"  Full SHA : {commit.sha}")
    print(f"  Message  : {commit.commit.message.strip()}")
    print(f"  Author   : {commit.commit.author.name}")
    print(f"  Date     : {commit.commit.author.date}")
    print()