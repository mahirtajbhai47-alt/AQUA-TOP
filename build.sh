#!/usr/bin/env bash
# Render build script. Exit immediately on error.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Collect static assets for WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Load sample catalogue data (safe to re-run; remove if not wanted)
python manage.py seed_data
