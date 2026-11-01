# Project 11 – Modular Digital Banking Core

## 1. Project overview

This project implements a small, reusable banking library in Python. It demonstrates
functions, positional and keyword arguments, default arguments, `*args`, `**kwargs`,
multiple return values, local/global scope and LEGB-related name lookup.

**Important:** This is an educational command-line demonstration. It is not connected
to a real bank and must not be used to store real customer or financial information.

## 2. Requirements

- Python 3.10 or newer
- No third-party packages are required
- Any Python editor or terminal (VS Code is suitable)

## 3. Project files

| File | Purpose |
|---|---|
| `banking_core.py` | Reusable banking functions and data classes |
| `main.py` | Command-line demonstration importing the module |
| `test_banking_core.py` | Automated tests using `unittest` |
| `uml_class_diagram.puml` | UML class diagram in PlantUML format |

## 4. Banking functions

1. `open_account()` – creates an account.
2. `deposit()` – adds money to an account.
3. `withdraw()` – withdraws money if sufficient funds exist.
4. `transfer()` – moves money between two different accounts.
5. `simple_interest()` – calculates simple interest.
6. `compound_interest()` – calculates compound interest.
7. `calculate_emi()` – calculates a monthly loan instalment.
8. `statement()` – returns transaction history with optional filters.
9. `fraud_check()` – flags transactions that exceed a configured limit.

Money is represented with Python's `Decimal` type to avoid common binary floating-point
rounding issues. Invalid amounts are rejected, and withdrawals/transfers cannot create
an overdraft.

## 5. Python concepts demonstrated

### Five argument types

- **Positional:** `open_account("A100", "Aarav", 500)`
- **Keyword:** `deposit(account, 100, description="Fee refund")`
- **Default:** `open_account("A101", "Mira")` uses an opening deposit of zero.
- **Variable positional (`*args`):** `statement(account, 10, 11)` accepts month numbers.
- **Variable keyword (`**kwargs`):** `statement(account, kind="deposit", min_amount=100)` accepts filters.

### Multiple return values

Banking operations return tuples such as `(success, message, new_balance)`.
The caller unpacks them:

```python
success, message, new_balance = deposit(account, 500)
```

### Scope

`transaction_counter` is a module-level variable. `legacy_record_transaction()`
uses the `global` keyword to demonstrate changing it. This is deliberately marked
as a legacy teaching example.

The normal `_record()` helper stores transaction history on the individual account.
This avoids a shared global counter in ordinary banking operations.

`scope_demo()` creates a local variable with the same name as the global variable.
The local name hides the global name inside that function. The module-level value is
read explicitly with `globals()` for demonstration.

Python's LEGB lookup order is Local, Enclosing, Global and Built-in. `legb_demo()` uses nested functions to demonstrate all four levels: a local variable, an enclosing variable, a module-level global name, and the built-in `len()` function.

## 6. How to run the project

Open the project folder in VS Code. Open its terminal in that folder.

Run the command-line demo:

```bash
python main.py
```

Run the banking module directly (it also has a `__main__` guard):

```bash
python banking_core.py
```

Run all automated tests:

```bash
python -m unittest -v
```

No installation command or external dependency is needed.

## 7. Sample output

The exact timestamps and transaction details may vary.

```text
====================================================
             MODULAR DIGITAL BANKING CORE
====================================================
Account opened successfully.
Deposit successful. New balance: ₹6500.00
Withdrawal successful. New balance: ₹5750.00
Account opened successfully.
Transfer successful. Sender balance: ₹5250.00
Fraud check: Transaction flagged for review: limit exceeded.

Simple interest on ₹10,000 at 5% for 2 years: 1000.00
Compound interest on ₹10,000 at 5% compounded yearly for 2 years: 1025.00
EMI for ₹1,00,000 at 12% for 12 months: 8884.88

Transaction statement:
... | opening      | ₹5000.00 | Balance ₹5000.00 | Initial deposit
... | deposit      | ₹1500.00 | Balance ₹6500.00 | Cash deposit
... | withdrawal   | ₹750.00  | Balance ₹5750.00 | Cash withdrawal
... | transfer_out | ₹500.00  | Balance ₹5250.00 | Transfer to REVA1002

Demo completed.
```

## 8. Test coverage

The test suite covers account creation, default values, invalid account details,
successful deposits and withdrawals, zero/negative amounts, overdrafts, transfers,
interest calculations, EMI, invalid calculation inputs, statement filters,
fraud checks, local/global scope and the `global` keyword.

The suite contains more than 15 test methods and uses only Python's built-in
`unittest` framework.

## 9. UML diagram

Open `uml_class_diagram.puml` with a PlantUML-compatible viewer to render the
class diagram. The diagram represents `Account`, `Transaction`, their relationship,
and the banking module's public operations.

## 10. Limitations

This is a simplified academic project. It does not implement authentication,
database persistence, encryption, concurrency control, regulatory compliance,
real fraud detection, or integration with payment networks. The fraud check is
a basic threshold demonstration, not a production fraud-prevention system.
