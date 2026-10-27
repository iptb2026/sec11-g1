-- =====================================================================
-- Clears every transaction and puts each account back at its opening
-- deposit, so the demo starts from clean data. Users, accounts, roles,
-- banks, fee types, policies, sessions and audit logs are kept.
--
-- TAKE A BACKUP FIRST (backup.ps1). This deletes data and can't be undone
-- except by restoring that backup.
--
--     USE catarig;
--     SOURCE reset_transactions.sql;
--
-- Then, from Banking system/appserver:
--     python backfill_ledger.py --apply   -- writes each account's opening ledger row
--     python demo_data.py ...             -- adds demo transactions through the API
-- and check: SELECT * FROM account_balance_audit WHERE difference <> 0;  (no rows)
-- =====================================================================

START TRANSACTION;

-- Children first: nothing references these tables, but the order keeps
-- it obvious that only transaction data goes.
DELETE FROM ledger_entries;
DELETE FROM fee_records;
DELETE FROM interest_records;
DELETE FROM interbank_transfers;
DELETE FROM transfers;
DELETE FROM withdrawals;
DELETE FROM deposits;

-- Every account goes back to what it had when it was opened.
UPDATE accounts a
JOIN account_types at ON at.id = a.account_type_id
SET a.available_balance = at.opening_deposit,
    a.ledger_balance    = at.opening_deposit;

-- Nothing has been withdrawn today any more.
UPDATE withdrawal_limits SET daily_used_amount = 0;

COMMIT;

SELECT COUNT(*) AS accounts_reset, SUM(available_balance) AS total_balance FROM accounts;
