-- =====================================================================
-- Brings account types and withdrawal limits in line with seed.py.
--
-- Why: catarig's SAVINGS and PAYROLL types were created by hand on
-- 2026-08-13, before seed.py existed, and seed.py never overwrites a type
-- that already exists. So catarig's SAVINGS had no minimum balance, no
-- interest rate and no daily withdrawal limit, and no account had a
-- withdrawal_limits row. Since the backend enforces the minimum balance
-- and gives NEW accounts their type's daily limit, existing accounts need
-- the same.
--
-- opening_deposit is deliberately NOT changed: the existing accounts were
-- opened with 0, and account_balance_audit (and reset_transactions.sql /
-- backfill_ledger.py) use the type's current opening_deposit as what every
-- account was opened with. Changing it would make every SAVINGS account
-- show a difference in verify.sql section 6.
--
-- Safe to run more than once. Works on whichever schema is selected:
--
--     USE catarig;
--     SOURCE align_account_types.sql;
--
-- TAKE A BACKUP FIRST (backup.ps1).
-- =====================================================================

START TRANSACTION;

-- SAVINGS: seed.py's minimum balance, interest rate and daily limit.
UPDATE account_types
SET minimum_balance        = 500.00,
    annual_interest_rate   = 0.25,
    daily_withdrawal_limit = 50000.00
WHERE type_code = 'SAVINGS';

-- Every account whose type has a daily limit gets a withdrawal_limits row,
-- as the API does for new accounts. Accounts that already have one keep it.
INSERT INTO withdrawal_limits (account_id, daily_limit_amount, daily_used_amount, last_reset_date)
SELECT a.id, at.daily_withdrawal_limit, 0.00, CURDATE()
FROM accounts a
JOIN account_types at ON at.id = a.account_type_id
LEFT JOIN withdrawal_limits wl ON wl.account_id = a.id
WHERE wl.id IS NULL
  AND at.daily_withdrawal_limit > 0;

COMMIT;

-- Result: each type's rules, and each account's daily limit.
SELECT type_code, minimum_balance, opening_deposit, annual_interest_rate, daily_withdrawal_limit
FROM account_types ORDER BY id;

SELECT a.account_number, at.type_code, a.available_balance, wl.daily_limit_amount
FROM accounts a
JOIN account_types at ON at.id = a.account_type_id
LEFT JOIN withdrawal_limits wl ON wl.account_id = a.id
ORDER BY a.id;

-- Accounts already below their type's minimum balance (no rows = none).
-- Not an error, but they can't withdraw or transfer out until topped up.
SELECT a.account_number, at.type_code, a.available_balance, at.minimum_balance
FROM accounts a
JOIN account_types at ON at.id = a.account_type_id
WHERE a.available_balance < at.minimum_balance;
