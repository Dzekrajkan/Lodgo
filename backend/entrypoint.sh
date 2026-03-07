#!/bin/sh

sleep 5

if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Applying Alembic migrations..."
  alembic upgrade head

  echo "Seeding database..."
  python -m backend.seed
fi

exec "$@"