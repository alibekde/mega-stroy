from __future__ import annotations

import aiosqlite
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional


@dataclass(frozen=True)
class Db:
    path: str


@asynccontextmanager
async def connect(db: Db) -> AsyncIterator[aiosqlite.Connection]:
    conn = await aiosqlite.connect(db.path)
    try:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        await conn.execute("PRAGMA journal_mode = WAL;")
        yield conn
        await conn.commit()
    finally:
        await conn.close()


async def migrate(db: Db) -> None:
    async with connect(db) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              full_name TEXT NOT NULL,
              phone TEXT NOT NULL UNIQUE,
              chat_id INTEGER UNIQUE,
              status TEXT NOT NULL DEFAULT 'active', -- active|inactive
              total_spent INTEGER NOT NULL DEFAULT 0,
              level TEXT NOT NULL DEFAULT 'Bronze', -- Bronze|Silver|Gold
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
              amount INTEGER NOT NULL,
              product TEXT NOT NULL,
              comment TEXT NOT NULL DEFAULT '',
              sale_date TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rewards (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
              reward_type TEXT NOT NULL, -- threshold|manual
              reward_name TEXT NOT NULL,
              note TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
              kind TEXT NOT NULL, -- sale|bonus|monthly|system
              message TEXT NOT NULL,
              created_at TEXT NOT NULL,
              delivered_at TEXT
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              actor_telegram_id INTEGER,
              actor_role TEXT NOT NULL, -- admin|customer|system
              action TEXT NOT NULL,
              meta_json TEXT NOT NULL,
              at TEXT NOT NULL
            );
            """
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer_date ON sales(customer_id, sale_date);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_rewards_customer ON rewards(customer_id);")


async def fetchval(conn: aiosqlite.Connection, sql: str, args: tuple[Any, ...] = ()) -> Any:
    cur = await conn.execute(sql, args)
    row = await cur.fetchone()
    return None if row is None else row[0]


async def fetchone(conn: aiosqlite.Connection, sql: str, args: tuple[Any, ...] = ()) -> Optional[aiosqlite.Row]:
    cur = await conn.execute(sql, args)
    return await cur.fetchone()


async def fetchall(conn: aiosqlite.Connection, sql: str, args: tuple[Any, ...] = ()) -> list[aiosqlite.Row]:
    cur = await conn.execute(sql, args)
    return await cur.fetchall()

