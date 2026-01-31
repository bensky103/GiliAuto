#!/bin/bash
# Start the Lead Automation Service

set -e

# Run migrations
alembic upgrade head

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
