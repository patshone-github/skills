#!/bin/bash

# Git Setup Script for Claude Skills Repository
# This script helps you initialize and push to your GitHub repository

echo "📦 Claude Skills Repository - Git Setup"
echo "======================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📂 Initializing git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# Add all files
echo ""
echo "📝 Adding files to git..."
git add .
echo "✓ Files added"

# Create initial commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit: M&A Tracker skill and marketplace structure" || {
    echo "ℹ️  Nothing to commit or commit already exists"
}

# Set up remote
echo ""
echo "🔗 Setting up GitHub remote..."
echo "Current remotes:"
git remote -v

if git remote | grep -q "origin"; then
    echo ""
    echo "⚠️  Origin already exists. Current URL:"
    git remote get-url origin
    echo ""
    read -p "Do you want to update it to https://github.com/patshone-github/skills.git? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin https://github.com/patshone-github/skills.git
        echo "✓ Remote updated"
    fi
else
    git remote add origin https://github.com/patshone-github/skills.git
    echo "✓ Remote added"
fi

# Push to GitHub
echo ""
echo "🚀 Ready to push to GitHub!"
echo ""
echo "To push your repository, run:"
echo "  git push -u origin main"
echo ""
echo "If your default branch is 'master', use:"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "📌 Repository URL: https://github.com/patshone-github/skills"
echo ""

# Show status
echo "Current git status:"
echo "-------------------"
git status --short

echo ""
echo "✅ Setup complete! Your repository is ready to push to GitHub."
