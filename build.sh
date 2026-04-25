#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
# This safely updates the schema without deleting existing data
echo "Running migrations..."
python -m alembic upgrade head
