from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Optional

from .db import Db, connect, fetchall, fetchone, fetchval
from .utils import json_dumps, now_iso


BONUS_50M = 50_000_000
BONUS_100M = 100_000_000


def compute_level(total_spent: int) -> str:
    if total_spent >= 50_000_000:
        return "Gold"
    if total_spent >= 10_000_000:
        return "Silver"
    return "Bronze"


@dataclass(frozen=True)
class Customer:
    id: int
    full_name: str
    phone: str
    chat_id: Optional[int]
    status: str
    total_spent: int
    level: str


async def audit(db: Db, *, actor_telegram_id: Optional[int], actor_role: str, action: str, meta: dict[str, Any], tz: str) -> None:
    async with connect(db) as conn:
        await conn.execute(
            "INSERT INTO audit_logs(actor_telegram_id, actor_role, action, meta_json, at) VALUES(?,?,?,?,?)",
            (actor_telegram_id, actor_role, action, json_dumps(meta), now_iso(tz)),
        )


async def create_customer(db: Db, *, full_name: str, phone: str, chat_id: Optional[int], tz: str, actor_telegram_id: int) -> int:
    async with connect(db) as conn:
        created_at = now_iso(tz)
        updated_at = created_at
        cur = await conn.execute(
            """
            INSERT INTO customers(full_name, phone, chat_id, status, total_spent, level, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (full_name.strip(), phone.strip(), chat_id, "active", 0, "Bronze", created_at, updated_at),
        )
        cid = int(cur.lastrowid)
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="customer.create", meta={"customer_id": cid, "full_name": full_name, "phone": phone}, tz=tz)
    return cid


async def list_customers(db: Db, *, limit: int = 50) -> list[Customer]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            "SELECT id, full_name, phone, chat_id, status, total_spent, level FROM customers ORDER BY id DESC LIMIT ?",
            (limit,),
        )
    return [Customer(**dict(r)) for r in rows]


async def find_customer(db: Db, *, query: str, limit: int = 20) -> list[Customer]:
    q = f"%{query.strip()}%"
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            """
            SELECT id, full_name, phone, chat_id, status, total_spent, level
            FROM customers
            WHERE CAST(id AS TEXT) LIKE ? OR full_name LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (q, q, q, limit),
        )
    return [Customer(**dict(r)) for r in rows]


async def get_customer(db: Db, *, customer_id: int) -> Optional[Customer]:
    async with connect(db) as conn:
        row = await fetchone(
            conn,
            "SELECT id, full_name, phone, chat_id, status, total_spent, level FROM customers WHERE id=?",
            (customer_id,),
        )
    return None if row is None else Customer(**dict(row))


async def set_customer_status(db: Db, *, customer_id: int, status: str, tz: str, actor_telegram_id: int) -> None:
    async with connect(db) as conn:
        await conn.execute("UPDATE customers SET status=?, updated_at=? WHERE id=?", (status, now_iso(tz), customer_id))
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="customer.status", meta={"customer_id": customer_id, "status": status}, tz=tz)


async def link_customer_chat(db: Db, *, phone: str, chat_id: int, tz: str) -> Optional[int]:
    async with connect(db) as conn:
        row = await fetchone(conn, "SELECT id FROM customers WHERE phone=?", (phone.strip(),))
        if row is None:
            return None
        customer_id = int(row["id"])
        await conn.execute("UPDATE customers SET chat_id=?, updated_at=? WHERE id=?", (chat_id, now_iso(tz), customer_id))
    await audit(db, actor_telegram_id=chat_id, actor_role="customer", action="customer.link_chat", meta={"customer_id": customer_id, "phone": phone}, tz=tz)
    return customer_id


async def add_sale(
    db: Db,
    *,
    customer_id: int,
    amount: int,
    product: str,
    comment: str,
    sale_date: str,
    tz: str,
    actor_telegram_id: int,
) -> tuple[int, list[str]]:
    async with connect(db) as conn:
        created_at = now_iso(tz)
        cur = await conn.execute(
            """
            INSERT INTO sales(customer_id, amount, product, comment, sale_date, created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (customer_id, amount, product.strip(), (comment or "").strip(), sale_date, created_at),
        )
        sale_id = int(cur.lastrowid)

        total_spent = int(await fetchval(conn, "SELECT COALESCE(SUM(amount),0) FROM sales WHERE customer_id=?", (customer_id,)) or 0)
        level = compute_level(total_spent)
        await conn.execute("UPDATE customers SET total_spent=?, level=?, updated_at=? WHERE id=?", (total_spent, level, created_at, customer_id))

    await audit(
        db,
        actor_telegram_id=actor_telegram_id,
        actor_role="admin",
        action="sale.add",
        meta={"customer_id": customer_id, "sale_id": sale_id, "amount": amount, "product": product, "sale_date": sale_date},
        tz=tz,
    )

    earned = await check_threshold_rewards(db, customer_id=customer_id, tz=tz, actor_telegram_id=actor_telegram_id)
    return sale_id, earned


async def delete_last_sale(db: Db, *, customer_id: int, tz: str, actor_telegram_id: int) -> Optional[int]:
    async with connect(db) as conn:
        row = await fetchone(conn, "SELECT id, amount FROM sales WHERE customer_id=? ORDER BY id DESC LIMIT 1", (customer_id,))
        if row is None:
            return None
        sale_id = int(row["id"])
        await conn.execute("DELETE FROM sales WHERE id=?", (sale_id,))

        total_spent = int(await fetchval(conn, "SELECT COALESCE(SUM(amount),0) FROM sales WHERE customer_id=?", (customer_id,)) or 0)
        level = compute_level(total_spent)
        await conn.execute("UPDATE customers SET total_spent=?, level=?, updated_at=? WHERE id=?", (total_spent, level, now_iso(tz), customer_id))

    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="sale.delete_last", meta={"customer_id": customer_id, "sale_id": sale_id}, tz=tz)
    return sale_id


async def list_sales_for_customer(db: Db, *, customer_id: int, limit: int = 50) -> list[dict[str, Any]]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            """
            SELECT id, amount, product, comment, sale_date, created_at
            FROM sales
            WHERE customer_id=?
            ORDER BY sale_date DESC, id DESC
            LIMIT ?
            """,
            (customer_id, limit),
        )
    return [dict(r) for r in rows]


async def sales_between(db: Db, *, start_date: str, end_date: str) -> list[dict[str, Any]]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            """
            SELECT s.id, s.amount, s.product, s.comment, s.sale_date, c.id as customer_id, c.full_name, c.phone
            FROM sales s
            JOIN customers c ON c.id = s.customer_id
            WHERE s.sale_date BETWEEN ? AND ?
            ORDER BY s.sale_date DESC, s.id DESC
            """,
            (start_date, end_date),
        )
    return [dict(r) for r in rows]


async def monthly_report(db: Db, *, year: int, month: int) -> dict[str, Any]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    start_s = start.isoformat()
    end_s = end.isoformat()

    async with connect(db) as conn:
        total = int(await fetchval(conn, "SELECT COALESCE(SUM(amount),0) FROM sales WHERE sale_date BETWEEN ? AND ?", (start_s, end_s)) or 0)
        count = int(await fetchval(conn, "SELECT COUNT(1) FROM sales WHERE sale_date BETWEEN ? AND ?", (start_s, end_s)) or 0)
        top_rows = await fetchall(
            conn,
            """
            SELECT c.id as customer_id, c.full_name, c.phone, COALESCE(SUM(s.amount),0) as sum_amount
            FROM customers c
            LEFT JOIN sales s ON s.customer_id=c.id AND s.sale_date BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY sum_amount DESC
            LIMIT 5
            """,
            (start_s, end_s),
        )
        top5 = [dict(r) for r in top_rows]

        # Growth vs prev month
        prev_year = year if month > 1 else year - 1
        prev_month = month - 1 if month > 1 else 12
        prev_start = date(prev_year, prev_month, 1)
        prev_end = (date(prev_year, prev_month + 1, 1) - timedelta(days=1)) if prev_month != 12 else date(prev_year, 12, 31)
        prev_total = int(
            await fetchval(
                conn,
                "SELECT COALESCE(SUM(amount),0) FROM sales WHERE sale_date BETWEEN ? AND ?",
                (prev_start.isoformat(), prev_end.isoformat()),
            )
            or 0
        )
    growth_pct = 0.0
    if prev_total > 0:
        growth_pct = (total - prev_total) * 100.0 / prev_total

    return {
        "start": start_s,
        "end": end_s,
        "total": total,
        "count": count,
        "top5": top5,
        "prev_total": prev_total,
        "growth_pct": growth_pct,
    }


async def check_threshold_rewards(db: Db, *, customer_id: int, tz: str, actor_telegram_id: int) -> list[str]:
    """50m -> Chang yutqich, 100m -> Super yutuq. Only once each."""
    async with connect(db) as conn:
        total = int(await fetchval(conn, "SELECT total_spent FROM customers WHERE id=?", (customer_id,)) or 0)
        existing = await fetchall(conn, "SELECT reward_name FROM rewards WHERE customer_id=? AND reward_type='threshold'", (customer_id,))
        have = {r["reward_name"] for r in existing}

        earned: list[str] = []
        if total >= BONUS_100M and "Super yutuq" not in have:
            earned.append("Super yutuq")
        if total >= BONUS_50M and "Chang yutqich" not in have:
            earned.append("Chang yutqich")

        for name in earned:
            await conn.execute(
                "INSERT INTO rewards(customer_id, reward_type, reward_name, note, created_at) VALUES(?,?,?,?,?)",
                (customer_id, "threshold", name, "", now_iso(tz)),
            )

    if earned:
        await audit(
            db,
            actor_telegram_id=actor_telegram_id,
            actor_role="admin",
            action="reward.threshold_earned",
            meta={"customer_id": customer_id, "earned": earned},
            tz=tz,
        )
    return earned


async def add_manual_reward(db: Db, *, customer_id: int, reward_name: str, note: str, tz: str, actor_telegram_id: int) -> int:
    async with connect(db) as conn:
        cur = await conn.execute(
            "INSERT INTO rewards(customer_id, reward_type, reward_name, note, created_at) VALUES(?,?,?,?,?)",
            (customer_id, "manual", reward_name.strip(), (note or "").strip(), now_iso(tz)),
        )
        rid = int(cur.lastrowid)
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="reward.manual_add", meta={"customer_id": customer_id, "reward_id": rid, "reward_name": reward_name}, tz=tz)
    return rid


async def list_rewards(db: Db, *, customer_id: int, limit: int = 50) -> list[dict[str, Any]]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            """
            SELECT id, reward_type, reward_name, note, created_at
            FROM rewards
            WHERE customer_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (customer_id, limit),
        )
    return [dict(r) for r in rows]


async def get_customer_by_chat(db: Db, *, chat_id: int) -> Optional[Customer]:
    async with connect(db) as conn:
        row = await fetchone(
            conn,
            "SELECT id, full_name, phone, chat_id, status, total_spent, level FROM customers WHERE chat_id=?",
            (chat_id,),
        )
    return None if row is None else Customer(**dict(row))


async def active_customers_with_chat(db: Db) -> list[Customer]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            "SELECT id, full_name, phone, chat_id, status, total_spent, level FROM customers WHERE status='active' AND chat_id IS NOT NULL",
        )
    return [Customer(**dict(r)) for r in rows]


async def all_customers_with_chat(db: Db) -> list[Customer]:
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            "SELECT id, full_name, phone, chat_id, status, total_spent, level FROM customers WHERE chat_id IS NOT NULL",
        )
    return [Customer(**dict(r)) for r in rows]


async def customers_inactive_days(db: Db, *, days: int, tz: str) -> list[Customer]:
    """No sales in last N days (or no sales ever)."""
    # We'll compare by sale_date (YYYY-MM-DD)
    cutoff = (datetime.now().date() - timedelta(days=days)).isoformat()
    async with connect(db) as conn:
        rows = await fetchall(
            conn,
            """
            SELECT c.id, c.full_name, c.phone, c.chat_id, c.status, c.total_spent, c.level
            FROM customers c
            LEFT JOIN (
              SELECT customer_id, MAX(sale_date) AS last_sale_date
              FROM sales
              GROUP BY customer_id
            ) ls ON ls.customer_id = c.id
            WHERE (ls.last_sale_date IS NULL OR ls.last_sale_date < ?) AND c.status='active'
            """,
            (cutoff,),
        )
    return [Customer(**dict(r)) for r in rows]


async def delete_sale_by_id(db: Db, *, sale_id: int, tz: str, actor_telegram_id: int) -> Optional[int]:
    async with connect(db) as conn:
        row = await fetchone(conn, "SELECT id, customer_id FROM sales WHERE id=?", (sale_id,))
        if row is None:
            return None
        cid = int(row["customer_id"])
        await conn.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        total_spent = int(await fetchval(conn, "SELECT COALESCE(SUM(amount),0) FROM sales WHERE customer_id=?", (cid,)) or 0)
        level = compute_level(total_spent)
        await conn.execute("UPDATE customers SET total_spent=?, level=?, updated_at=? WHERE id=?", (total_spent, level, now_iso(tz), cid))
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="sale.delete_by_id", meta={"sale_id": sale_id, "customer_id": cid}, tz=tz)
    return sale_id


async def delete_reward(db: Db, *, reward_id: int, tz: str, actor_telegram_id: int) -> Optional[int]:
    async with connect(db) as conn:
        row = await fetchone(conn, "SELECT id, customer_id FROM rewards WHERE id=?", (reward_id,))
        if row is None:
            return None
        cid = int(row["customer_id"])
        await conn.execute("DELETE FROM rewards WHERE id=?", (reward_id,))
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="reward.delete", meta={"reward_id": reward_id, "customer_id": cid}, tz=tz)
    return reward_id


async def delete_customer(db: Db, *, customer_id: int, tz: str, actor_telegram_id: int) -> bool:
    async with connect(db) as conn:
        row = await fetchone(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
        if row is None:
            return False
        await conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    await audit(db, actor_telegram_id=actor_telegram_id, actor_role="admin", action="customer.delete", meta={"customer_id": customer_id}, tz=tz)
    return True

