"""Command-line demonstration that imports the reusable banking module."""

from banking_core import (
    calculate_emi,
    compound_interest,
    deposit,
    fraud_check,
    open_account,
    simple_interest,
    statement,
    transfer,
    withdraw,
)


def main() -> None:
    """Run the sample banking workflow."""
    print("=" * 52)
    print("             MODULAR DIGITAL BANKING CORE")
    print("=" * 52)

    ok, message, student_account = open_account(
        "REVA1001", "Aarav Sharma", 5000
    )
    print(message)
    if not ok or student_account is None:
        return

    ok, message, balance = deposit(student_account, 1500)
    print(f"{message} New balance: ₹{balance}")

    ok, message, balance = withdraw(student_account, 750)
    print(f"{message} New balance: ₹{balance}")

    ok, message, savings_account = open_account(
        "REVA1002", "Mira Rao", 1000
    )
    print(message)
    if ok and savings_account is not None:
        ok, message, balance = transfer(student_account, savings_account, 500)
        print(f"{message} Sender balance: ₹{balance}")

    flagged, fraud_message = fraud_check(60000)
    print(f"Fraud check: {fraud_message}")

    print("\nSimple interest on ₹10,000 at 5% for 2 years:",
          simple_interest(10000, 5, 2))
    print("Compound interest on ₹10,000 at 5% compounded yearly for 2 years:",
          compound_interest(10000, 5, 1, 2))
    print("EMI for ₹1,00,000 at 12% for 12 months:",
          calculate_emi(100000, 12, 12))

    print("\nTransaction statement:")
    for item in statement(student_account):
        print(f"{item.timestamp:%Y-%m-%d %H:%M} | {item.kind:12} "
              f"| ₹{item.amount} | Balance ₹{item.balance_after} "
              f"| {item.description}")

    print("\nDemo completed.")


if __name__ == "__main__":
    main()
