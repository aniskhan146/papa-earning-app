#!/bin/bash

# Check if a commit message was provided as an argument
if [ -z "$1" ]
then
  echo "❌ Error: Please provide a commit message."
  echo "👉 Usage: ./update-pro.sh \"Your update message\""
  exit 1
fi

echo "🔄 Preparing to update with message: $1"

git add .
git commit -m "$1"
git push

echo "✅ Success! Your GitHub repository has been updated."