#!/bin/sh

set -e

echo "Waiting for PostgreSQL to start..."
python <<EOF
import time
import psycopg2
import os

while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        )
        conn.close()
        break
    except Exception:
        print("PostgreSQL not ready yet. Waiting...")
        time.sleep(1)
EOF

echo "PostgreSQL is up. Running Alembic migrations..."
alembic upgrade head

echo "Starting daily stats worker..."
python worker.py &

echo "Starting FastAPI app..."
fastapi run
