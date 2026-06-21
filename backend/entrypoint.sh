#!/bin/sh
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Applying Alembic migrations..."
  alembic -c backend/alembic.ini upgrade head

  echo "Seeding database..."
  python -m backend.seed
fi

exec "$@"