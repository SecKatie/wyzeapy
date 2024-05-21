#!/bin/bash

# Bump the version in the package.json file
poetry version patch

# Get the new version
version=$(poetry version -s)

# Create a new branch
git checkout -b release/$version

# Commit the change
git add .
git commit -m "chore(pyproject.toml): Bumps version to $version"

# Push the branch
git push origin release/$version