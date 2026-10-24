-- =====================================================================
-- Database health check for the Mini Banking System.
--
-- Run against the team database before every demo/presentation and
-- after any big testing session:
--
--     USE catarig;
--     SOURCE verify.sql;
--
-- Every check uses DATABASE(), so it works on whichever schema is
-- selected. Each section says what a "good" result looks like.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. All 17 tables exist.
--    Good: tables_found = 17 and missing_tables is NULL.
-- ---------------------------------------------------------------------
SELECT
  COUNT(t.TABLE_NAME) AS tables_found,
  NULLIF(GROUP_CONCAT(CASE WHEN t.TABLE_NAME IS NULL THEN e.name END), '') AS missing_tables
FROM (
            SELECT 'roles' AS name
  UNION ALL SELECT 'account_types'
  UNION ALL SELECT 'banks'
  UNION ALL SELECT 'fee_types'
  UNION ALL SELECT 'users'
  UNION ALL SELECT 'sessions'
  UNION ALL SELECT 'audit_logs'
  UNION ALL SELECT 'accounts'
  UNION ALL SELECT 'withdrawal_limits'
  UNION ALL SELECT 'interest_policies'
  UNION ALL SELECT 'deposits'
  UNION ALL SELECT 'withdrawals'
  UNION ALL SELECT 'transfers'
  UNION ALL SELECT 'interbank_transfers'
  UNION ALL SELECT 'fee_records'
  UNION ALL SELECT 'interest_records'
  UNION ALL SELECT 'ledger_entries'
) e
LEFT JOIN information_schema.TABLES t
  ON t.TABLE_SCHEMA = DATABASE() AND t.TABLE_NAME = e.name;


-- ---------------------------------------------------------------------
-- 2. Every foreign key in app/models/ is a real FOREIGN KEY constraint.
--    The models define 20. Good: no rows returned.
--    A row here means the database was built from an old script, not
--    from the models — that relationship is only checked in Python.
-- ---------------------------------------------------------------------
SELECT e.tbl AS table_name, e.col AS column_name, e.ref_tbl AS should_reference
FROM (
            SELECT 'users' AS tbl, 'role_id' AS col, 'roles' AS ref_tbl
  UNION ALL SELECT 'sessions', 'user_id', 'users'
  UNION ALL SELECT 'audit_logs', 'user_id', 'users'
  UNION ALL SELECT 'accounts', 'customer_id', 'users'
  UNION ALL SELECT 'accounts', 'account_type_id', 'account_types'
  UNION ALL SELECT 'withdrawal_limits', 'account_id', 'accounts'
  UNION ALL SELECT 'interest_policies', 'account_type_id', 'account_types'
  UNION ALL SELECT 'deposits', 'account_id', 'accounts'
  UNION ALL SELECT 'deposits', 'deposited_by_user_id', 'users'
  UNION ALL SELECT 'withdrawals', 'account_id', 'accounts'
  UNION ALL SELECT 'withdrawals', 'approved_by_user_id', 'users'
  UNION ALL SELECT 'transfers', 'source_account_id', 'accounts'
  UNION ALL SELECT 'transfers', 'destination_account_id', 'accounts'
  UNION ALL SELECT 'interbank_transfers', 'source_account_id', 'accounts'
  UNION ALL SELECT 'interbank_transfers', 'target_bank_id', 'banks'
  UNION ALL SELECT 'fee_records', 'account_id', 'accounts'
  UNION ALL SELECT 'fee_records', 'fee_type_id', 'fee_types'
  UNION ALL SELECT 'interest_records', 'account_id', 'accounts'
  UNION ALL SELECT 'interest_records', 'policy_id', 'interest_policies'
  UNION ALL SELECT 'ledger_entries', 'account_id', 'accounts'
) e
LEFT JOIN information_schema.KEY_COLUMN_USAGE k
  ON k.TABLE_SCHEMA = DATABASE()
 AND k.TABLE_NAME = e.tbl
 AND k.COLUMN_NAME = e.col
 AND k.REFERENCED_TABLE_NAME = e.ref_tbl
WHERE k.CONSTRAINT_NAME IS NULL;


-- ---------------------------------------------------------------------
-- 3. Row counts across every table, at a glance.
--    Good for a demo: roles, account_types, banks, fee_types, users and
--    accounts are all above 0 (seed.py fills these).
-- ---------------------------------------------------------------------
SELECT 'roles' AS tbl, COUNT(*) AS cnt FROM roles
UNION ALL SELECT 'account_types', COUNT(*) FROM account_types
UNION ALL SELECT 'banks', COUNT(*) FROM banks
UNION ALL SELECT 'fee_types', COUNT(*) FROM fee_types
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL SELECT 'withdrawal_limits', COUNT(*) FROM withdrawal_limits
UNION ALL SELECT 'interest_policies', COUNT(*) FROM interest_policies
UNION ALL SELECT 'deposits', COUNT(*) FROM deposits
UNION ALL SELECT 'withdrawals', COUNT(*) FROM withdrawals
UNION ALL SELECT 'transfers', COUNT(*) FROM transfers
UNION ALL SELECT 'interbank_transfers', COUNT(*) FROM interbank_transfers
UNION ALL SELECT 'fee_records', COUNT(*) FROM fee_records
UNION ALL SELECT 'interest_records', COUNT(*) FROM interest_records
UNION ALL SELECT 'ledger_entries', COUNT(*) FROM ledger_entries;


-- ---------------------------------------------------------------------
-- 4. No plain-text passwords. A bcrypt hash always starts with $2.
--    Good: no rows returned. A row here means that user cannot log in
--    (this broke login more than once this semester).
-- ---------------------------------------------------------------------
SELECT id, username, LEFT(hashed_password, 4) AS starts_with
FROM users
WHERE hashed_password NOT LIKE '$2%';


-- ---------------------------------------------------------------------
-- 5. Every role has at least one ACTIVE user, so each role can be demoed.
--    Good: active_users > 0 for ADMIN, STAFF and CUSTOMER.
-- ---------------------------------------------------------------------
SELECT r.role_code, COUNT(u.id) AS active_users
FROM roles r
LEFT JOIN users u ON u.role_id = r.id AND u.account_status = 'ACTIVE'
GROUP BY r.role_code
ORDER BY r.role_code;


-- ---------------------------------------------------------------------
-- 6. Balances reconcile with the transactions behind them.
--    Needs account_balance_audit.sql to have been run once.
--    Good: no rows returned.
-- ---------------------------------------------------------------------
SELECT account_id, account_number, owner, current_balance, expected_balance, difference
FROM account_balance_audit
WHERE difference <> 0;


-- ---------------------------------------------------------------------
-- 7. The ledger agrees with each balance.
--    Every balance change writes a ledger row (since PR #19), so an
--    account's credits minus debits should equal its balance.
--    Good: no rows returned.
--    ledger_entries = 0 means the account's transactions predate the
--    automatic ledger: run `python backfill_ledger.py` in appserver.
-- ---------------------------------------------------------------------
SELECT a.id AS account_id, a.account_number, a.available_balance,
       COALESCE(l.ledger_total, 0) AS ledger_total,
       COALESCE(l.entries, 0)      AS ledger_entries
FROM accounts a
LEFT JOIN (SELECT account_id,
                  SUM(credit_amount - debit_amount) AS ledger_total,
                  COUNT(*) AS entries
           FROM ledger_entries GROUP BY account_id) l
       ON l.account_id = a.id
WHERE COALESCE(l.ledger_total, 0) <> a.available_balance;


-- ---------------------------------------------------------------------
-- 8. The balance floor is in place (migration 0002_balance_checks).
--    Good: 2 rows, chk_accounts_available_balance and
--    chk_accounts_ledger_balance. None: run `alembic upgrade head`.
-- ---------------------------------------------------------------------
SELECT CONSTRAINT_NAME, CHECK_CLAUSE
FROM information_schema.CHECK_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = DATABASE()
  AND CONSTRAINT_NAME LIKE 'chk_accounts_%';


-- ---------------------------------------------------------------------
-- 9. Every account whose type has a daily withdrawal limit has its
--    withdrawal_limits row (the API creates it for new accounts).
--    Good: no rows returned. Rows: run align_account_types.sql.
-- ---------------------------------------------------------------------
SELECT a.id AS account_id, a.account_number, at.type_code, at.daily_withdrawal_limit
FROM accounts a
JOIN account_types at ON at.id = a.account_type_id
LEFT JOIN withdrawal_limits wl ON wl.account_id = a.id
WHERE wl.id IS NULL
  AND at.daily_withdrawal_limit > 0;
