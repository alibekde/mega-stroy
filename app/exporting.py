from __future__ import annotations

from io import BytesIO
from typing import Any

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .utils import fmt_amount


def customers_to_xlsx(customers: list[dict[str, Any]]) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Customers"
    ws.append(["ID", "Ism", "Telefon", "Status", "Jami savdo", "Level", "Chat ID"])
    for c in customers:
        ws.append([c["id"], c["full_name"], c["phone"], c["status"], c["total_spent"], c["level"], c["chat_id"]])
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio


def sales_to_xlsx(sales: list[dict[str, Any]]) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["ID", "Sana", "Summa", "Mahsulot", "Izoh", "Mijoz ID", "Mijoz", "Telefon"])
    for s in sales:
        ws.append([s.get("id"), s.get("sale_date"), s.get("amount"), s.get("product"), s.get("comment"), s.get("customer_id"), s.get("full_name"), s.get("phone")])
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio


def customers_to_pdf(customers: list[dict[str, Any]], title: str = "Mijozlar ro'yxati") -> BytesIO:
    bio = BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, title)
    y -= 30
    c.setFont("Helvetica", 10)

    for row in customers:
        line = f"#{row['id']}  {row['full_name']}  {row['phone']}  [{row['status']}]  {fmt_amount(int(row['total_spent']))}  {row['level']}"
        c.drawString(40, y, line[:120])
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
    c.showPage()
    c.save()
    bio.seek(0)
    return bio

