-- =====================================================================
-- account_balance_audit: every account's balance next to the balance
-- its transactions say it should have.
--
-- Create (or refresh) it once per database:
--
--     USE catarig;
--     SOURCE account_balance_audit.sql;
--
-- Then anyone can run:
--
--     SELECT * FROM account_balance_audit;                   -- all accounts
--     SELECT * FROM account_balance_audit WHERE difference <> 0;  -- problems only
--
-- How expected_balance is built — it mirrors what the API routers do:
--   + account type's opening_deposit   (accounts.py sets this on create)
--   + deposits                          (deposits.py)
--   - withdrawals                       (withdrawals.py)
--   - fee records                       (fee_records.py)
--   + interest records                  (interest_records.py)
--   - transfers out, + transfers in     (transfers.py, every status)
--   - interbank transfers + their fee   (interbank_transfers.py; FAILED and
--                                        REVERSED are refunded, so not counted)
--
-- Since PR #19 a DELETE reverses the money and removes the row, and a PUT
-- can't change an amount, so both keep this view at 0.
--
-- A non-zero difference usually means one of:
--   * a transaction was edited or deleted before PR #19, when PUT/DELETE
--     did not adjust the balance
--   * an interbank transfer was marked FAILED/REVERSED before the refund
--     fix, so it was never refunded
--   * the account type's opening_deposit was changed after the account
--     was opened
--   * a balance was changed directly in MySQL
--
-- The ledger has its own check: verify.sql section 7.
-- =====================================================================

CREATE OR REPLACE VIEW account_balance_audit AS
SELECT
  a.id                AS account_id,
  a.account_number,
  u.username          AS owner,
  a.status,
  a.available_balance AS current_balance,
  at.opening_deposit
    + COALESCE(d.total, 0)
    - COALESCE(w.total, 0)
    - COALESCE(f.total, 0)
    + COALESCE(i.total, 0)
    - COALESCE(t_out.total, 0)
    + COALESCE(t_in.total, 0)
    - COALESCE(ib.total, 0) AS expected_balance,
  a.available_balance - (
    at.opening_deposit
    + COALESCE(d.total, 0)
    - COALESCE(w.total, 0)
    - COALESCE(f.total, 0)
    + COALESCE(i.total, 0)
    - COALESCE(t_out.total, 0)
    + COALESCE(t_in.total, 0)
    - COALESCE(ib.total, 0)
  ) AS difference
FROM accounts a
JOIN users u          ON u.id = a.customer_id
JOIN account_types at ON at.id = a.account_type_id
LEFT JOIN (SELECT account_id, SUM(amount) AS total
           FROM deposits GROUP BY account_id) d
       ON d.account_id = a.id
LEFT JOIN (SELECT account_id, SUM(amount) AS total
           FROM withdrawals GROUP BY account_id) w
       ON w.account_id = a.id
LEFT JOIN (SELECT account_id, SUM(amount_charged) AS total
           FROM fee_records GROUP BY account_id) f
       ON f.account_id = a.id
LEFT JOIN (SELECT account_id, SUM(amount_credited) AS total
           FROM interest_records GROUP BY account_id) i
       ON i.account_id = a.id
LEFT JOIN (SELECT source_account_id AS account_id, SUM(amount) AS total
           FROM transfers GROUP BY source_account_id) t_out
       ON t_out.account_id = a.id
LEFT JOIN (SELECT destination_account_id AS account_id, SUM(amount) AS total
           FROM transfers GROUP BY destination_account_id) t_in
       ON t_in.account_id = a.id
LEFT JOIN (SELECT source_account_id AS account_id, SUM(amount + COALESCE(transfer_fee, 0)) AS total
           FROM interbank_transfers
           WHERE status NOT IN ('FAILED', 'REVERSED')
           GROUP BY source_account_id) ib
       ON ib.account_id = a.id;
