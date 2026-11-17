"""Safely copy a JanSahay SQLite database into the configured Supabase DB.

Run from the backend directory. The default is a read-only dry run; pass
--apply only when the destination contains no JanSahay application data.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone

from sqlalchemy import MetaData, Table, create_engine, inspect, select, text, func

from app.database.session import Base, engine, ensure_schemas
from app.models import models  # noqa: F401 - register every model on Base.metadata


MIGRATION_TABLE = "sqlite_migration_runs"
MIGRATION_SCHEMA = "credentials"
BATCH_SIZE = 500


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def target_row_count(connection, table):
    inspector = inspect(connection)
    if not inspector.has_table(table.name, schema=table.schema):
        return 0
    qualified = f'"{table.schema}"."{table.name}"' if table.schema else f'"{table.name}"'
    return connection.execute(text(f"SELECT count(*) FROM {qualified}")).scalar_one()


def main():
    parser = argparse.ArgumentParser(description="Copy the local JanSahay SQLite database to Supabase PostgreSQL.")
    parser.add_argument(
        "--source",
        default=os.path.join(os.path.dirname(__file__), "jansahay.db"),
        help="Path to the source SQLite database (defaults to backend/jansahay.db).",
    )
    parser.add_argument("--apply", action="store_true", help="Apply the copy; without this flag, only show a dry run.")
    args = parser.parse_args()

    source_path = os.path.abspath(args.source)
    if not os.path.isfile(source_path):
        raise SystemExit(f"SQLite source database not found: {source_path}")
    if engine.dialect.name != "postgresql":
        raise SystemExit("DATABASE_URL must point to Supabase PostgreSQL. Check backend/.env.")

    source_hash = sha256_file(source_path)
    migration_id = f"sqlite-sha256:{source_hash}"
    source_engine = create_engine(f"sqlite:///{source_path}")
    source_inspector = inspect(source_engine)
    source_tables = set(source_inspector.get_table_names())
    ordered_tables = list(Base.metadata.sorted_tables)

    with engine.connect() as target:
        target_inspector = inspect(target)
        marker_exists = target_inspector.has_table(MIGRATION_TABLE, schema=MIGRATION_SCHEMA)
        already_done = False
        if marker_exists:
            already_done = target.execute(
                text(
                    f'SELECT 1 FROM "{MIGRATION_SCHEMA}"."{MIGRATION_TABLE}" '
                    "WHERE migration_id = :migration_id"
                ),
                {"migration_id": migration_id},
            ).first() is not None

        source_counts = {}
        with source_engine.connect() as source:
            for table_name in sorted(source_tables):
                reflected = Table(table_name, MetaData(), autoload_with=source_engine)
                source_counts[table_name] = source.execute(
                    select(func.count()).select_from(reflected)
                ).scalar_one()

        target_counts = {table.fullname: target_row_count(target, table) for table in ordered_tables}

    summary = {
        "source_file": source_path,
        "source_sha256": source_hash,
        "destination_host": engine.url.host,
        "destination_database": engine.url.database,
        "source_row_counts": source_counts,
        "destination_row_counts_before": target_counts,
    }

    if already_done:
        print(json.dumps({**summary, "status": "ALREADY_MIGRATED"}, indent=2))
        return

    populated = {name: count for name, count in target_counts.items() if count}
    if populated:
        raise SystemExit(
            "Destination already contains JanSahay rows; refusing to merge or overwrite them. "
            f"Existing counts: {populated}"
        )

    if not args.apply:
        print(json.dumps({**summary, "status": "DRY_RUN", "next_step": "Re-run with --apply to copy into the empty destination."}, indent=2))
        return

    ensure_schemas()
    Base.metadata.create_all(bind=engine)
    copied_counts = {}
    with engine.begin() as target:
        target.execute(
            text(
                f'''CREATE TABLE IF NOT EXISTS "{MIGRATION_SCHEMA}"."{MIGRATION_TABLE}" (
                    migration_id TEXT PRIMARY KEY,
                    source_file TEXT NOT NULL,
                    source_sha256 TEXT NOT NULL,
                    completed_at TIMESTAMPTZ NOT NULL,
                    row_counts JSONB NOT NULL
                )'''
            )
        )
        # Recheck under the write transaction in case another process started a migration.
        if target.execute(
            text(
                f'SELECT 1 FROM "{MIGRATION_SCHEMA}"."{MIGRATION_TABLE}" '
                "WHERE migration_id = :migration_id"
            ),
            {"migration_id": migration_id},
        ).first():
            print(json.dumps({**summary, "status": "ALREADY_MIGRATED"}, indent=2))
            return

        for target_table in ordered_tables:
            if target_table.name not in source_tables:
                copied_counts[target_table.fullname] = 0
                continue

            source_table = Table(target_table.name, MetaData(), autoload_with=source_engine)
            source_columns = {column.name for column in source_table.columns}
            target_columns = {column.name for column in target_table.columns}
            shared_columns = [column.name for column in target_table.columns if column.name in source_columns and column.name in target_columns]
            copied = 0
            with source_engine.connect() as source:
                result = source.execution_options(stream_results=True).execute(
                    select(*(source_table.c[name] for name in shared_columns))
                )
                while batch := result.mappings().fetchmany(BATCH_SIZE):
                    records = [dict(row) for row in batch]
                    target.execute(target_table.insert(), records)
                    copied += len(records)
            copied_counts[target_table.fullname] = copied

        # Keep generated integer primary keys above the copied IDs.
        for target_table in ordered_tables:
            if target_table.schema is None:
                continue
            integer_pks = [column for column in target_table.primary_key.columns if column.autoincrement is True or column.autoincrement == "auto"]
            for column in integer_pks:
                seq = target.execute(
                    text("SELECT pg_get_serial_sequence(:table_name, :column_name)"),
                    {"table_name": f"{target_table.schema}.{target_table.name}", "column_name": column.name},
                ).scalar_one_or_none()
                if seq:
                    max_id = target.execute(select(func.max(column))).scalar_one_or_none()
                    target.execute(
                        text("SELECT setval(CAST(:sequence_name AS regclass), :last_value, :is_called)"),
                        {"sequence_name": seq, "last_value": max_id or 1, "is_called": max_id is not None},
                    )

        verified_counts = {table.fullname: target_row_count(target, table) for table in ordered_tables}
        for table in ordered_tables:
            source_count = source_counts.get(table.name, 0)
            if verified_counts[table.fullname] != source_count:
                raise RuntimeError(
                    f"Row count mismatch for {table.fullname}: source={source_count}, destination={verified_counts[table.fullname]}"
                )

        target.execute(
            text(
                f'INSERT INTO "{MIGRATION_SCHEMA}"."{MIGRATION_TABLE}" '
                "(migration_id, source_file, source_sha256, completed_at, row_counts) "
                "VALUES (:migration_id, :source_file, :source_sha256, :completed_at, CAST(:row_counts AS jsonb))"
            ),
            {
                "migration_id": migration_id,
                "source_file": source_path,
                "source_sha256": source_hash,
                "completed_at": datetime.now(timezone.utc),
                "row_counts": json.dumps(verified_counts),
            },
        )

    print(json.dumps({**summary, "status": "SUCCESS", "copied_row_counts": copied_counts}, indent=2))
    source_engine.dispose()


if __name__ == "__main__":
    main()
