#!/usr/bin/env bash
set -e

echo "[entrypoint] Wait for DB…"
python - <<'PY'
import os, sys, time
import psycopg2
url = os.getenv("SYNC_DB_URL") or os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DB_URL")
if not url:
    print("No DB URL provided", file=sys.stderr); sys.exit(1)
for i in range(30):
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print("DB is ready.")
        break
    except Exception as e:
        print(f"DB not ready ({e}), retry {i+1}/30…")
        time.sleep(2)
else:
    print("DB not reachable", file=sys.stderr); sys.exit(1)
PY

echo "[entrypoint] Run migrations…"
cd my_bot/
alembic upgrade head

echo "[entrypoint] Start bot…"
python bot.py
