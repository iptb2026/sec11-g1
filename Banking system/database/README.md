# Database Admin Runbook — Mini Banking System

Everything the Database Admins need for the team database, in one folder. Connection settings come from `appserver/.env` (MySQL, schema `catarig`, `127.0.0.1:3306`, user `admin`), read by `appserver/app/core/config.py`. Run `python make_env.py` in `appserver` to create `appserver/.env` (it asks for the DB password and generates a `SECRET_KEY`), or copy `appserver/.env.example` to `appserver/.env` and fill them in by hand; `.env` is git-ignored, so secrets never go into git. If MySQL runs in Docker on a different port, change `DB_PORT` there; the API, Alembic and `seed.py` all read the same file.

The team's MySQL (8.0) runs inside the **`ipt2-g1-home`** Docker container, which does not publish port 3306 to Windows. Run the backend, `alembic` and `seed.py` **inside that container** (where `127.0.0.1:3306` is correct), and pass `-Container ipt2-g1-home` to `backup.ps1`.

| File | What it is |
|---|---|
| `verify.sql` | Health check: tables, foreign keys, row counts, plain-text passwords, demo users per role, balance reconciliation, ledger vs balance, balance floor |
| `account_balance_audit.sql` | Creates the `account_balance_audit` view: each account's balance next to what its transactions say it should be |
| `reset_transactions.sql` | Clears every transaction and puts accounts back at their opening deposit, for a clean demo (section 2) |
| `../appserver/backfill_ledger.py` | Writes the ledger rows missing for transactions made before the ledger was automatic (PR #19) |
| `../appserver/demo_data.py` | Creates demo customers, accounts and transactions **through the API** |
| `../appserver/set_password.py` | Sets a user's password, e.g. `admin` before a demo |
| `backup.ps1` | Dumps the database to `database/backups/` (git-ignored, dumps contain password hashes) |
| `ERD.md` | Entity-Relationship Diagram of all 17 tables, generated from the models |
| `../appserver/migrations/` | Alembic migrations (schema changes, tracked in git) |
| `../appserver/seed.py` | Demo data: roles, users, account types, banks, fee types, interest policy, one customer account |

All commands below run from `Banking system/appserver` with its virtual environment active, unless they say otherwise.

---

## 1. Setting up a database

**New, empty database** (creates all 17 tables, then the demo data):

```powershell
pip install -r requirements.txt
alembic upgrade head
python seed.py
```

**Database that already has the tables** (the API or `seed.py` created them with `create_all`). Tell Alembic which revision it is at, without touching any table, then bring it up to date:

```powershell
alembic stamp 0001_baseline   # tables made before 2026-10-24 (like catarig)
alembic upgrade head          # adds the balance floor (0002_balance_checks)
python seed.py                # only adds what is missing
```

Tables made by `create_all` on or after 2026-10-24 already have the balance floor, so stamp those with `alembic stamp head` instead.

**The team `catarig` database** is already stamped at `0001_baseline`, so it only needs `alembic upgrade head`. If an account is below 0 the upgrade stops with error 3819 and tells you how to find it.

Then, in MySQL (from the `database` folder), create the audit view once:

```sql
USE catarig;
SOURCE account_balance_audit.sql;
```

### Demo logins (from `seed.py`, password `password123`)

| Username | Role | Has |
|---|---|---|
| `admin` | ADMIN | Admin pages |
| `teller1` | STAFF | Staff pages |
| `jdelacruz` | CUSTOMER | Savings account `1000000001` |
| `auditor1` | AUDITOR | Every admin and operations page, read-only |

`seed.py` never changes rows that already exist; use `set_password.py` to change a password.

The team `catarig` database was reset to clean demo data on 2026-10-24 (section 2). Every login there uses `password123`, including the demo customers `lmercado` and `preyes` from `demo_data.py`. Its known-good backup is `backups/catarig_20261024_1702_KNOWN_GOOD.sql`.

---

## 2. Before every demo or presentation

### Once: clean demo data

The team database still holds test transactions (including a −500.00 deposit made before negative amounts were blocked). To start the demo from clean, realistic data:

1. Take a backup (section 3).
2. Clear the test transactions, in MySQL from the `database` folder:
   ```sql
   USE catarig;
   SOURCE reset_transactions.sql;
   ```
3. From `appserver`, write each account's opening ledger row and set a known admin password:
   ```powershell
   python backfill_ledger.py --apply
   python set_password.py admin
   ```
4. Start the backend, then add demo transactions through the API (`--api` is the backend address, through NGINX if it runs there):
   ```powershell
   python demo_data.py --password <the admin password from step 3>
   ```
   This creates customers `lmercado` and `preyes` (password `password123`), a savings account each, deposits, a withdrawal, a transfer between them and an interbank transfer to BDO.
5. Run `verify.sql` (below), then take a backup and name it as the team's **known-good** copy. Share it outside git (e.g. the team's Google Drive) so anyone can restore it before the demo.

To keep the existing transactions instead, run only `python backfill_ledger.py` (dry run first, then `--apply`) so the old transactions get their ledger rows.

### Every time

1. Take a backup (section 3).
2. Run the health check and read each result against the "Good:" line in the file:
   ```sql
   USE catarig;
   SOURCE verify.sql;
   ```
   The two checks that most often catch real problems:
   - **Plain-text passwords:** any row means that user cannot log in.
   - **Balances:** any row from `account_balance_audit` means an account's balance no longer matches its transactions (see section 5).
   - **Ledger:** any row in section 7 means the ledger doesn't add up to the balance. `ledger_entries = 0` only means old transactions without ledger rows: run `backfill_ledger.py`.

---

## 3. Backups and restore

From the `database` folder in PowerShell:

```powershell
.\backup.ps1                          # MySQL installed on this PC
.\backup.ps1 -Container <name>        # MySQL in Docker (find the name with: docker ps)
.\backup.ps1 -Port 3501               # any setting from config.py can be overridden
```

It asks for the MySQL password and writes `backups\catarig_<yyyyMMdd_HHmm>.sql`.

Restore (this replaces the current data):

```powershell
mysql -h 127.0.0.1 -P 3306 -u admin -p catarig < backups\<file>.sql
```

Keep one **known-good** backup taken right after `seed.py` plus a few test transactions, and share it with the team outside git. That is the copy to restore before a demo.

---

## 4. Changing the schema (Alembic)

`create_all` only creates missing tables; it never adds a column to a table that already exists. Every schema change from now on goes through Alembic so everyone's database stays the same:

1. Edit the model in `app/models/`.
2. Generate the migration (compares the models with your database):
   ```powershell
   alembic revision --autogenerate -m "add deleted_at to users"
   ```
3. **Read the new file in `migrations/versions/`** before using it. Autogenerate misses some things (for example renamed columns show up as drop + add, which loses data).
4. Apply it: `alembic upgrade head`
5. Commit the model change and the migration file together.

Teammates then only run `alembic upgrade head` after pulling. `alembic current` shows which revision a database is at; `alembic downgrade -1` undoes the last migration.

---

## 5. Status of the Database Admin guide

| Guide item | Status |
|---|---|
| Foreign keys are real constraints | **Done in the models.** All 20 relationships are `FOREIGN KEY`s when the tables come from the models or Alembic. `verify.sql` check 2 confirms it on the live database (needed if it was ever built from an old SQL script). |
| Balance reconciliation | **Done.** `account_balance_audit` covers deposits, withdrawals, fees, interest, transfers in/out and interbank transfers + fee, not just the first four. |
| Backups | **Done.** `backup.ps1`. |
| Seed data | **Done.** `seed.py` now covers every reference table and one customer account. |
| A. Migrations (Alembic) | **Done.** Baseline `0001_baseline` creates exactly what `create_all` creates (checked table by table). |
| B. Indexes | **Not needed as written.** The guide's four columns (`users.username`, `accounts.account_number`, `deposits.reference_number`, `transfers.transfer_reference`) are already `UNIQUE`, and MySQL indexes every unique column and every foreign key. Adding them again creates duplicate indexes. Revisit only if a specific non-unique search becomes slow. The team database already has one such duplicate, `idx_interbank_reference` (same column as the unique `reference_number` index). It is declared in the model so Alembic leaves it alone; dropping it is safe but a team call. |
| C. Balance floor `CHECK` | **Done.** Migration `0002_balance_checks` adds `CHECK (available_balance >= 0)` and `CHECK (ledger_balance >= 0)` on `accounts` (also declared in the model). Every endpoint that changes a balance commits through `commit_money` (`app/core/db_utils.py`), which turns MySQL error 3819 into a 400 and rolls back. `verify.sql` section 8 confirms it on the live database. |
| D. Balance audit view | **Done**, as a real reconciliation (the guide's version only listed balances). |
| E. Soft delete | **Team decision.** Changes every `DELETE` endpoint; raise with Backend before doing anything. |
| F. ERD | **Done.** `ERD.md`. |

### Issues found that affect balances (for Backend)

These are why `account_balance_audit` can show a difference even when nobody touched MySQL directly:

1. **Fixed: editing or deleting a transaction keeps the balance right.** `PUT` on deposits, withdrawals, transfers and fee records can only change descriptive fields (remarks, channel...); changing an amount or an account returns 400. `DELETE` on deposits, withdrawals, transfers, interbank transfers, fee records and interest records reverses the balance change (and writes a `REVERSAL` ledger row). Edits or deletes made *before* this fix still show up in `account_balance_audit`.
2. **Fixed: failed or reversed interbank transfers are now refunded.** `PUT /interbank-transfers/{id}/status` to `FAILED` or `REVERSED` returns amount + fee to the source account, and those statuses can no longer change (no double refund). This is the fix from `personal/suan/appserver`, ported. Transfers marked FAILED/REVERSED *before* this fix were never refunded, so they will show up in `account_balance_audit` as a negative difference of amount + fee.

---

## Ownership split (two Database Admins)

| Admin 1 — schema | Admin 2 — data |
|---|---|
| Alembic migrations, reviewing every schema change | Running `verify.sql`, investigating balance mismatches |
| Constraints and indexes (items B, C, E above) | Backups, the known-good restore copy |
| Keeping `ERD.md` current after schema changes | `seed.py` and demo-ready test data |
