from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AdminCustomerAdd(StatesGroup):
    full_name = State()
    phone = State()


class AdminCustomerSearch(StatesGroup):
    query = State()


class AdminSelectCustomer(StatesGroup):
    query = State()


class AdminSaleAdd(StatesGroup):
    customer_query = State()
    amount = State()
    product = State()
    comment = State()
    date = State()


class AdminReportMonthly(StatesGroup):
    year_month = State()  # YYYY-MM


class AdminReportCustomerHistory(StatesGroup):
    customer_query = State()


class AdminReportRange(StatesGroup):
    start = State()  # YYYY-MM-DD
    end = State()


class AdminBroadcast(StatesGroup):
    audience = State()  # all|active
    text = State()


class AdminManualReward(StatesGroup):
    customer_query = State()
    reward_name = State()
    note = State()


class AdminExportSalesRange(StatesGroup):
    start = State()
    end = State()


class AdminCustomerDelete(StatesGroup):
    customer_query = State()


class AdminRewardDelete(StatesGroup):
    customer_query = State()
    reward_id = State()


class AdminSaleDeleteById(StatesGroup):
    sale_id = State()

