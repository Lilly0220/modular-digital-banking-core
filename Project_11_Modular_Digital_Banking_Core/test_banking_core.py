"""Automated tests for the modular digital banking core."""

import unittest
from decimal import Decimal

import banking_core as bank


class BankingCoreTests(unittest.TestCase):
    """Test account operations, calculations, validation and scope."""

    def setUp(self):
        ok, message, self.account = bank.open_account("A100", "Test User", 1000)
        self.assertTrue(ok, message)
        ok, message, self.other = bank.open_account("A200", "Second User", 500)
        self.assertTrue(ok, message)

    def test_open_account_success(self):
        ok, message, account = bank.open_account("A300", "New User", 250)
        self.assertTrue(ok)
        self.assertEqual(account.balance, Decimal("250.00"))

    def test_open_account_default_initial_deposit(self):
        ok, _, account = bank.open_account("A301", "No Deposit")
        self.assertTrue(ok)
        self.assertEqual(account.balance, Decimal("0.00"))

    def test_open_account_invalid_number(self):
        ok, _, account = bank.open_account(" ", "Name")
        self.assertFalse(ok)
        self.assertIsNone(account)

    def test_open_account_negative_initial_deposit(self):
        ok, _, account = bank.open_account("A302", "Name", -10)
        self.assertFalse(ok)
        self.assertIsNone(account)

    def test_deposit_success_and_tuple_return(self):
        ok, message, balance = bank.deposit(self.account, 200)
        self.assertTrue(ok)
        self.assertEqual(balance, Decimal("1200.00"))
        self.assertIsInstance(message, str)

    def test_deposit_keyword_only_description(self):
        ok, _, _ = bank.deposit(self.account, 25, description="Campus refund")
        self.assertTrue(ok)
        self.assertEqual(self.account.transactions[-1].description, "Campus refund")

    def test_deposit_zero_is_invalid(self):
        ok, _, balance = bank.deposit(self.account, 0)
        self.assertFalse(ok)
        self.assertEqual(balance, Decimal("1000.00"))

    def test_deposit_negative_is_invalid(self):
        ok, _, balance = bank.deposit(self.account, -5)
        self.assertFalse(ok)
        self.assertEqual(balance, Decimal("1000.00"))

    def test_withdraw_success(self):
        ok, _, balance = bank.withdraw(self.account, 300)
        self.assertTrue(ok)
        self.assertEqual(balance, Decimal("700.00"))

    def test_withdraw_overdraft_is_rejected(self):
        ok, message, balance = bank.withdraw(self.account, 1500)
        self.assertFalse(ok)
        self.assertIn("Insufficient funds", message)
        self.assertEqual(balance, Decimal("1000.00"))

    def test_withdraw_invalid_amount(self):
        ok, _, balance = bank.withdraw(self.account, -1)
        self.assertFalse(ok)
        self.assertEqual(balance, Decimal("1000.00"))

    def test_transfer_success_updates_both_accounts(self):
        ok, _, sender_balance = bank.transfer(self.account, self.other, 200)
        self.assertTrue(ok)
        self.assertEqual(sender_balance, Decimal("800.00"))
        self.assertEqual(self.other.balance, Decimal("700.00"))

    def test_transfer_overdraft_rejected_without_changes(self):
        ok, _, sender_balance = bank.transfer(self.account, self.other, 2000)
        self.assertFalse(ok)
        self.assertEqual(sender_balance, Decimal("1000.00"))
        self.assertEqual(self.other.balance, Decimal("500.00"))

    def test_transfer_same_account_rejected(self):
        ok, _, balance = bank.transfer(self.account, self.account, 10)
        self.assertFalse(ok)
        self.assertEqual(balance, Decimal("1000.00"))

    def test_simple_interest(self):
        self.assertEqual(bank.simple_interest(10000, 5, 2), Decimal("1000.00"))

    def test_simple_interest_negative_rate_rejected(self):
        with self.assertRaises(ValueError):
            bank.simple_interest(10000, -1, 2)

    def test_compound_interest(self):
        self.assertEqual(
            bank.compound_interest(10000, 10, 1, 2), Decimal("2100.00")
        )

    def test_compound_interest_invalid_frequency(self):
        with self.assertRaises(ValueError):
            bank.compound_interest(10000, 5, 0, 2)

    def test_emi_zero_interest(self):
        self.assertEqual(bank.calculate_emi(1200, 0, 12), Decimal("100.00"))

    def test_emi_positive_interest(self):
        self.assertGreater(bank.calculate_emi(100000, 12, 12), Decimal("8000.00"))

    def test_emi_invalid_months(self):
        with self.assertRaises(ValueError):
            bank.calculate_emi(10000, 5, 0)

    def test_statement_with_varargs_and_kwargs(self):
        bank.deposit(self.account, 100, description="Monthly allowance")
        bank.deposit(self.account, 250, description="Scholarship")
        result = bank.statement(
            self.account, self.account.transactions[-1].timestamp.month,
            kind="deposit", min_amount=200
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].description, "Scholarship")

    def test_statement_unknown_filter_rejected(self):
        with self.assertRaises(ValueError):
            bank.statement(self.account, status="success")

    def test_statement_invalid_month_rejected(self):
        with self.assertRaises(ValueError):
            bank.statement(self.account, 13)

    def test_fraud_check_passes_under_limit(self):
        flagged, _ = bank.fraud_check(1000, daily_total=2000)
        self.assertFalse(flagged)

    def test_fraud_check_flags_over_limit(self):
        flagged, message = bank.fraud_check(60000)
        self.assertTrue(flagged)
        self.assertIn("flagged", message.lower())

    def test_fraud_check_flags_daily_total_limit(self):
        flagged, _ = bank.fraud_check(1000, daily_total=49500)
        self.assertTrue(flagged)

    def test_scope_demo_local_hides_global(self):
        local_value, global_value = bank.scope_demo()
        self.assertEqual(local_value, "local counter")
        self.assertIsInstance(global_value, int)

    def test_legb_demo(self):
        local_name, enclosing_name, global_length, builtin_length = bank.legb_demo()
        self.assertEqual(local_name, "local scope")
        self.assertEqual(enclosing_name, "enclosing scope")
        self.assertEqual(global_length, len("global scope"))
        self.assertEqual(builtin_length, 4)

    def test_legacy_global_counter_increments(self):
        before = bank.transaction_counter
        bank.legacy_record_transaction(self.account, "test", 10, "Scope test")
        self.assertEqual(bank.transaction_counter, before + 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
