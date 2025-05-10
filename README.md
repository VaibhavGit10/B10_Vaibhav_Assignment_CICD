# 📌 Assignment_05_DevOps: Building CI-CD Pipeline Tool

## 📖 Overview
This project demonstrates a basic Continuous Integration and Continuous Deployment (CI/CD) pipeline using a custom-built toolchain. The objective is to automatically deploy a static HTML website hosted on a GitHub repository to an Nginx web server running on an AWS EC2 or local Linux instance.

The pipeline follows these steps:
1. A static HTML project is created and version-controlled via GitHub.
2. A web server environment is prepared using Nginx on a remote instance.
3. A Python script interacts with the GitHub API to detect new commits.
4. A Bash script handles code deployment by cloning the latest repository version and restarting the Nginx server.
5. A cron job is scheduled to periodically check for updates and trigger deployment.
6. The complete setup is tested by committing changes to the repository and observing the automatic update on the server.

This setup emulates core CI/CD principles and provides a foundational understanding of automating deployments without using third-party CI/CD tools.

## 📌 Task 1: Set Up a Simple HTML Project
Create a simple HTML project and push it to a GitHub repository.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CI/CD Demo Page</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
      background-color: #f2f2f2;
    }
    h1 {
      color: #333;
    }
    p {
      font-size: 18px;
      color: #555;
    }
  </style>
</head>
<body>
  <h1>Welcome to the CI/CD Pipeline Demo</h1>
  <p>This is a simple HTML page deployed using a CI/CD pipeline using GitHub, Python, Bash, and Crontab!</p>
  <p>This project is deployed by Vaibhav Pawar</p>
</body>
</html>
```

#### 📸 Output Screenshots

![Img_01](https://github.com/user-attachments/assets/b1bc4e63-c9c5-4388-82b9-e9dda6c1db87)
![Img_02](https://github.com/user-attachments/assets/018b67d0-f716-4dee-a69a-03198dabdbed)


## 📌 Task 2: Set Up an AWS EC2/Local Linux Instance with Nginx
Set up an AWS EC2 instance or a local Linux instance and install Nginx to serve the HTML content.

#### 📸 Output Screenshots

![Img_03](https://github.com/user-attachments/assets/32279b8e-658f-4108-be6b-f7e911fb84bd)
![Img_04](https://github.com/user-attachments/assets/baef3fa3-9f62-43b7-aff2-f6ddc6e8758e)


## :warning: Create `secret_key.env` File

Follow these steps to create the `secret_key.env` file, which is required in the deployment scripts:

### **Important Note:**
- **Fork the repository** and **generate your own Personal Access Token (PAT)** from GitHub. 
- If you've named your forked repository differently, **update the `REPOSITORY_NAME`** below accordingly.

### Run the following commands to create the `secret_key.env` file:

```bash
nano secret_key.env
```

Then add the following content:
```bash
ACCESS_TOKEN=INPUT_YOUR_CLASSIC_GITHUB_PAT_TOKEN_HERE
REPOSITORY_NAME=VaibhavGit10/B10_Vaibhav_Assignment_CICD
```

Note: Ensure to replace INPUT_YOUR_CLASSIC_GITHUB_PAT_TOKEN_HERE with your actual GitHub PAT token and update the REPOSITORY_NAME if necessary.

## 📌 Task 3: Write a Python Script to Check for New Commits
Create a Python script that uses the GitHub API to check for new commits in the repository.

Copy the File Name for the Python File
```python
check_commits.py
```

Copy the Code for the Python File
```python
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
        print("�� New commits detected.")
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
```

#### 📸 Output Screenshots

![Img_09](https://github.com/user-attachments/assets/6ea107c7-bc78-4976-8616-897c23ed5e40)
![Img_10](https://github.com/user-attachments/assets/22328610-d752-4be9-af18-6d0ac8b5b79a)


## 📌 Task 4: Write a Bash Script to Deploy the Code
Create a bash script that:
- Clones the latest code from the GitHub repository.
- Restarts Nginx to serve the new version of the site.

Copy the File Name for the Bash Script
```bash
deploy.sh
```

Copy the Code for the Bash Script
```bash
#!/bin/bash

# Load environment variables
export GITHUB_TOKEN="your_token"
export REPO_OWNER="VaibhavGit10"
export REPO_NAME="B10_Vaibhav_Assignment_CICD"
export LAST_COMMIT_FILE="/home/ubuntu/cicd/last_commit.txt"
export REPO_DIR="/home/ubuntu/cicd/B10_Vaibhav_Assignment_CICD"

# Execute the Python deployment script
python3 /home/ubuntu/cicd/auto_deploy.py

```

#### 📸 Output Screenshots

![Img_10](https://github.com/user-attachments/assets/3249a73e-a7f3-44d8-b638-0734d74a1bdb)


## 📌 Task 5: Set Up a Cron Job to Run the Python Script
Create a cron job that runs the Python script at regular intervals to check for new commits.

## :lock: Ensure Correct Permissions for Scripts

To avoid permission issues while running the deployment scripts, you need to update the file permissions. Run the following commands to grant the necessary access:

### Run the following commands:

```bash
sudo chmod 666 check_commits.py
sudo chmod 666 deploy.sh
```


## 📌 Task 6: Test the Setup
Make a new commit to the GitHub repository and verify that the changes are automatically deployed and served via Nginx.



## 📜 License
This project is licensed under the Apache License.

## 🤝 Contributing
Feel free to fork and improve the scripts! ⭐ If you find this project useful, please consider starring the repo—it really helps and supports my work! 😊

## 📧 Contact
For any queries, reach out via GitHub Issues.

---

🎯 **Thank you for reviewing this project! 🚀**
