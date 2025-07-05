#!/bin/bash

# Bump the version in the pyproject.toml file
uv run hatch version patch

# Get the new version
version=$(uv run hatch version)

# Create a new branch
git checkout -b release/$version

# Commit the change
git add .
git commit -m "chore(pyproject.toml): Bumps version to $version"

# Push the branch
git push origin release/$version