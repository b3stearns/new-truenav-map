#!/bin/bash

# Set GitHub repository details
REPO_URL=https://$GITHUB_TOKEN@github.com/$GITHUB_REPO.git
COMMIT_MESSAGE="Update map data $(date -u)"

# Navigate to working directory
cd /app || exit 1

# Initialize Git repository if it doesn't exist
if [ ! -d ".git" ]; then
    git init
    git remote add origin $REPO_URL
    # Create an initial commit if the repository is empty
    git add .
    git commit -m "Initial commit" || true
fi

# Configure git
git config --global user.email "bot@example.com"
git config --global user.name "Map Update Bot"

# Add and commit changes
git add connections_map.html data.json
git commit -m "$COMMIT_MESSAGE" || {
    echo "No changes to commit"
    exit 0
}

# Push to GitHub
git push origin $BRANCH || {
    # If push fails, try pulling and merging first
    git pull --rebase origin $BRANCH
    git push origin $BRANCH
}

echo "Pushed updated map to GitHub"