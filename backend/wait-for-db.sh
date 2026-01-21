#!/bin/sh
set -e

until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for $DB_HOST:$DB_PORT..."
  sleep 1
done

echo "Database is ready!"
exec "$@"
