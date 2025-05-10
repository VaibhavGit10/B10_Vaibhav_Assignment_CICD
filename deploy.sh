#!/bin/bash

# Load environment variables
export GITHUB_TOKEN="your_token"
export REPO_OWNER="VaibhavGit10"
export REPO_NAME="B10_Vaibhav_Assignment_CICD"
export LAST_COMMIT_FILE="/home/ubuntu/cicd/last_commit.txt"
export REPO_DIR="/home/ubuntu/cicd/B10_Vaibhav_Assignment_CICD"

# Load environment variables
# Load environment variables
export GITHUB_TOKEN="your_token"
export REPO_OWNER="VaibhavGit10"
export REPO_NAME="B10_Vaibhav_Assignment_CICD"
export LAST_COMMIT_FILE="/home/ubuntu/cicd/last_commit.txt"
export REPO_DIR="/home/ubuntu/cicd/B10_Vaibhav_Assignment_CICD"

# Execute the Python deployment script
python3 /home/ubuntu/cicd/auto_deploy.py
