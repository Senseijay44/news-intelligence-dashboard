import os
import time

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
TIMEOUT_SECONDS = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
SLEEP_SECONDS = float(os.getenv("DB_WAIT_INTERVAL", "2"))

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is required for DB readiness check")

start = time.time()
last_error = None

while time.time() - start < TIMEOUT_SECONDS:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database is ready")
        raise SystemExit(0)
    except Exception as exc:  # noqa: BLE001
        last_error = exc
        print(f"Waiting for database... ({exc})")
        time.sleep(SLEEP_SECONDS)

raise SystemExit(f"Database was not ready within {TIMEOUT_SECONDS}s: {last_error}")
