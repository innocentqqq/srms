#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
# If poetry is used, it will handle it, otherwise use pip
if [ -f pyproject.toml ]; then
    poetry install
else
    pip install -r requirements.txt
fi

# Run database migrations
# We use the python path to ensure we use the environment's alembic
python -m alembic upgrade head
