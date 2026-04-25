#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# If we are on Render and the database has old tables, we might need to reset
# You can remove the 'python reset_db.py' line after one successful deployment
if [ "$RENDER" = "true" ]; then
    echo "Running database reset check for Render..."
    python reset_db.py
fi

# Run database migrations
echo "Running migrations..."
python -m alembic upgrade head
