# Database Admin Runbook — Mini Banking System

Everything the Database Admins need for the team database, in one folder. Connection settings come from `appserver/app/core/config.py` (MySQL, schema `catarig`, `127.0.0.1:3306`, user `admin`). If MySQL runs in Docker on a different port, change it there; Alembic and `seed.py` read the same file.

The team's MySQL (8.0) runs inside the **`ipt2-g1-home`** Docker container, which does not publish port 3306 to Windows. Run the backend, `alembic` and `seed.py` **inside that container** (where `127.0.0.1:3306` is correct), and pass `-Container ipt2-g1-home` to `backup.ps1`.

| File | What it is |
|---|---|
| `verify.sql` | Health check: tables, foreign keys, row counts, plain-text passwords, demo users per role, balance reconciliation |
| `account_balance_audit.sql` | Creates the `account_balance_audit` view: each account's balance next to what its transactions say it should be |
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

**Database that already has the tables** (the API or `seed.py` created them with `create_all`). Tell Alembic it is already at the baseline, without touching any table:

```powershell
alembic stamp 0001_baseline
python seed.py          # only adds what is missing
```

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
| `juandelacruz` | CUSTOMER | Savings account `1000-0000-0001`, opened with the `SAVINGS` type's opening deposit |

`seed.py` never changes rows that already exist. On the team `catarig` database that means:
- `admin` already existed, so it keeps **its old password**, not `password123`.
- `SAVINGS` already existed with an opening deposit of ₱0, so Juan's account opens at ₱0 (₱1,000 only on a fresh database). Deposit into it before a demo.
- The older customer `jdelacruz` (account `1000000001`) is still there next to `juandelacruz`.

---

## 2. Before every demo or presentation

1. Take a backup (section 3).
2. Run the health check and read each result against the "Good:" line in the file:
   ```sql
   USE catarig;
   SOURCE verify.sql;
   ```
   The two checks that most often catch real problems:
   - **Plain-text passwords:** any row means that user cannot log in.
   - **Balances:** any row from `account_balance_audit` means an account's balance no longer matches its transactions (see section 5).

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
| C. Balance floor `CHECK` | **Needs Backend first.** MySQL reports a `CHECK` violation as error 3819, which PyMySQL raises as `OperationalError`, not `IntegrityError`. `commit_or_409` only catches `IntegrityError`, and the balance updates use a plain `db.commit()`, so the API would return a 500. Backend must handle it before the constraint is added (as an Alembic migration). |
| D. Balance audit view | **Done**, as a real reconciliation (the guide's version only listed balances). |
| E. Soft delete | **Team decision.** Changes every `DELETE` endpoint; raise with Backend before doing anything. |
| F. ERD | **Done.** `ERD.md`. |

### Issues found that affect balances (for Backend)

These are why `account_balance_audit` can show a difference even when nobody touched MySQL directly:

1. **Editing or deleting a transaction does not adjust the balance.** `PUT`/`DELETE` on deposits, withdrawals, transfers and fee records, and `DELETE` on interest records, change only the record (the routers say so in their notes).
2. **Fixed: failed or reversed interbank transfers are now refunded.** `PUT /interbank-transfers/{id}/status` to `FAILED` or `REVERSED` returns amount + fee to the source account, and those statuses can no longer change (no double refund). This is the fix from `personal/suan/appserver`, ported. Transfers marked FAILED/REVERSED *before* this fix were never refunded, so they will show up in `account_balance_audit` as a negative difference of amount + fee.

---

## Ownership split (two Database Admins)

| Admin 1 — schema | Admin 2 — data |
|---|---|
| Alembic migrations, reviewing every schema change | Running `verify.sql`, investigating balance mismatches |
| Constraints and indexes (items B, C, E above) | Backups, the known-good restore copy |
| Keeping `ERD.md` current after schema changes | `seed.py` and demo-ready test data |
