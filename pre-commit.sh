#!/usr/bin/env bash

black --config=pyproject.toml .

git add .

ln -sf ../../pre-commit.sh .git/hooks/pre-commit