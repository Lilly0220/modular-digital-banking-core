"""Reusable functions for a small, educational digital banking core.

This module is a classroom demonstration, not production banking software.
It uses Decimal for money calculations and keeps transaction history on
each Account object rather than relying on shared global application state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")
transaction_counter = 0  # Used only by the legacy scope demonstration.


@dataclass
class Transaction:
    """Represent one recorded account transaction."""

    kind: str
    amount: Decimal
    balance_after: Decimal
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Account:
    """Represent a bank account and its own transaction history."""

    account_number: str
    holder_name: str
    balance: Decimal = Decimal("0.00")
    transactions: list[Transaction] = field(default_factory=list)


def _to_decimal(value: Any, field_name: str = "amount") -> Decimal:
    """Convert a supported numeric value to Decimal or raise ValueError."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a valid number.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_name} must be a valid number.") from None
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite.")
    return result


def validate_positive_amount(amount: Any) -> Decimal:
    """Return a money amount rounded to cents; reject zero and negatives."""
    value = _to_decimal(amount)
    if value <= 0:
        raise ValueError("Amount must be greater than zero.")
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def validate_non_negative_amount(amount: Any) -> Decimal:
    """Return a non-negative money amount rounded to cents."""
    value = _to_decimal(amount)
    if value < 0:
        raise ValueError("Amount cannot be negative.")
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _record(account: Account, kind: str, amount: Decimal,
            description: str) -> None:
    """Append a transaction to one account's own history."""
    account.transactions.append(
        Transaction(kind, amount, account.balance, description)
    )


def open_account(account_number: str, holder_name: str,
                 initial_deposit: Any = 0) -> tuple[bool, str, Account | None]:
    """Create an account, optionally with an initial deposit.

    Positional arguments: account_number, holder_name.
    Default argument: initial_deposit.
    Returns success, message and the new Account (or None).
    """
    if not isinstance(account_number, str) or not account_number.strip():
        return False, "Account number is required.", None
    if not isinstance(holder_name, str) or not holder_name.strip():
        return False, "Account holder name is required.", None
    try:
        opening_balance = validate_non_negative_amount(initial_deposit)
    except ValueError as error:
        return False, str(error), None

    account = Account(account_number.strip(), holder_name.strip(),
                      opening_balance)
    if opening_balance > 0:
        _record(account, "opening", opening_balance, "Initial deposit")
    return True, "Account opened successfully.", account


def deposit(account: Account, amount: Any, *,
            description: str = "Cash deposit") -> tuple[bool, str, Decimal]:
    """Deposit money; description is a keyword-only argument."""
    try:
        value = validate_positive_amount(amount)
    except ValueError as error:
        return False, str(error), account.balance
    account.balance += value
    _record(account, "deposit", value, description)
    return True, "Deposit successful.", account.balance


def withdraw(account: Account, amount: Any, *,
             description: str = "Cash withdrawal") -> tuple[bool, str, Decimal]:
    """Withdraw money if the account has sufficient funds."""
    try:
        value = validate_positive_amount(amount)
    except ValueError as error:
        return False, str(error), account.balance
    if value > account.balance:
        return False, "Insufficient funds: overdraft is not allowed.", account.balance
    account.balance -= value
    _record(account, "withdrawal", value, description)
    return True, "Withdrawal successful.", account.balance


def transfer(source: Account, destination: Account,
             amount: Any) -> tuple[bool, str, Decimal]:
    """Transfer money between two different accounts."""
    if source is destination or source.account_number == destination.account_number:
        return False, "Source and destination accounts must be different.", source.balance
    try:
        value = validate_positive_amount(amount)
    except ValueError as error:
        return False, str(error), source.balance
    if value > source.balance:
        return False, "Insufficient funds: transfer declined.", source.balance

    # Both balances are changed only after all validation succeeds.
    source.balance -= value
    destination.balance += value
    _record(source, "transfer_out", value,
            f"Transfer to {destination.account_number}")
    _record(destination, "transfer_in", value,
            f"Transfer from {source.account_number}")
    return True, "Transfer successful.", source.balance


def simple_interest(principal: Any, annual_rate: Any,
                    years: Any) -> Decimal:
    """Calculate simple interest (interest only), with rate as a percentage."""
    p = validate_non_negative_amount(principal)
    rate = _to_decimal(annual_rate, "annual_rate")
    duration = _to_decimal(years, "years")
    if rate < 0 or duration < 0:
        raise ValueError("Rate and years cannot be negative.")
    return (p * rate * duration / Decimal("100")).quantize(
        CENT, rounding=ROUND_HALF_UP
    )


def compound_interest(principal: Any, annual_rate: Any,
                      times_per_year: int, years: Any) -> Decimal:
    """Calculate compound interest earned, with rate as a percentage."""
    p = validate_non_negative_amount(principal)
    rate = _to_decimal(annual_rate, "annual_rate")
    duration = _to_decimal(years, "years")
    if rate < 0 or duration < 0:
        raise ValueError("Rate and years cannot be negative.")
    if not isinstance(times_per_year, int) or isinstance(times_per_year, bool):
        raise ValueError("times_per_year must be a positive integer.")
    if times_per_year <= 0:
        raise ValueError("times_per_year must be a positive integer.")
    periods = Decimal(times_per_year) * duration
    factor = Decimal("1") + rate / (Decimal("100") * times_per_year)
    final_amount = p * (factor ** int(periods))
    return (final_amount - p).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_emi(principal: Any, annual_rate: Any,
                  months: int) -> Decimal:
    """Calculate monthly loan EMI using a fixed monthly repayment formula."""
    p = validate_positive_amount(principal)
    rate = _to_decimal(annual_rate, "annual_rate")
    if rate < 0:
        raise ValueError("Annual rate cannot be negative.")
    if not isinstance(months, int) or isinstance(months, bool) or months <= 0:
        raise ValueError("Months must be a positive integer.")
    monthly_rate = rate / Decimal("1200")
    if monthly_rate == 0:
        return (p / months).quantize(CENT, rounding=ROUND_HALF_UP)
    factor = (Decimal("1") + monthly_rate) ** months
    emi = p * monthly_rate * factor / (factor - Decimal("1"))
    return emi.quantize(CENT, rounding=ROUND_HALF_UP)


def statement(account: Account, *months: int,
              **filters: Any) -> list[Transaction]:
    """Return transactions filtered by optional months and keyword filters.

    Variable-length positional arguments (*months) accept month numbers.
    Variable-length keyword arguments (**filters) accept kind,
    min_amount and description_contains.
    Example: statement(account, 10, 11, kind="deposit").
    """
    allowed = {"kind", "min_amount", "description_contains"}
    unknown = set(filters) - allowed
    if unknown:
        raise ValueError(f"Unknown statement filter(s): {', '.join(sorted(unknown))}")
    for month in months:
        if not isinstance(month, int) or isinstance(month, bool) or not 1 <= month <= 12:
            raise ValueError("Months must be integers from 1 to 12.")

    minimum = None
    if "min_amount" in filters:
        minimum = validate_non_negative_amount(filters["min_amount"])
    kind = filters.get("kind")
    description_text = filters.get("description_contains")

    results = []
    for item in account.transactions:
        if months and item.timestamp.month not in months:
            continue
        if kind is not None and item.kind != kind:
            continue
        if minimum is not None and item.amount < minimum:
            continue
        if description_text is not None and description_text.lower() not in item.description.lower():
            continue
        results.append(item)
    return results


def fraud_check(amount: Any, *, daily_total: Any = 0,
                transaction_limit: Any = 50000) -> tuple[bool, str]:
    """Flag a transaction when its amount or daily total exceeds a limit."""
    try:
        value = validate_positive_amount(amount)
        total = validate_non_negative_amount(daily_total)
        limit = validate_positive_amount(transaction_limit)
    except ValueError as error:
        return True, f"Transaction flagged: {error}"
    if value > limit or total + value > limit:
        return True, "Transaction flagged for review: limit exceeded."
    return False, "Transaction passed the basic fraud check."


def legacy_record_transaction(account: Account, kind: str,
                              amount: Any, description: str) -> None:
    """Demonstrate global mutation using the global keyword (legacy only)."""
    global transaction_counter
    value = validate_positive_amount(amount)
    _record(account, kind, value, description)
    transaction_counter += 1


def scope_demo() -> tuple[str, int]:
    """Show a local name hiding the module-level transaction_counter."""
    transaction_counter = "local counter"
    return transaction_counter, globals()["transaction_counter"]


def legb_demo() -> tuple[str, str, int, int]:
    """Demonstrate Local, Enclosing, Global and Built-in name lookup."""
    global_name = "global scope"

    def outer() -> tuple[str, str, int, int]:
        enclosing_name = "enclosing scope"

        def inner() -> tuple[str, str, int, int]:
            local_name = "local scope"
            # len is found in the Built-in scope.
            return local_name, enclosing_name, len(global_name), len("LEGB")

        return inner()

    return outer()


def main() -> None:
    """Run a small demonstration when this module is executed directly."""
    success, message, account = open_account("DEMO1001", "Demo Student", 1000)
    print(message)
    if not success or account is None:
        return
    success, message, balance = deposit(account, 250)
    print(message, "| Balance:", balance)
    success, message, balance = withdraw(account, 100)
    print(message, "| Balance:", balance)
    print("Statement entries:", len(statement(account)))
    print("Scope demonstration:", scope_demo())


if __name__ == "__main__":
    main()
