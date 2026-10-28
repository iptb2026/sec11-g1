"""
Write the ledger rows that are missing for transactions made before the
ledger was filled automatically (PR #19). Since #19 every balance change
writes its own ledger row; older deposits, withdrawals, transfers, fees,
interest and account openings have none.

Run from Banking system/appserver, after taking a backup:

    .\\virt\\Scripts\\python backfill_ledger.py           # dry run: only reports
    .\\virt\\Scripts\\python backfill_ledger.py --apply   # writes the rows

For every account it lists the money events behind its balance (the same
ones account_balance_audit adds up), replays them in date order, and
inserts a ledger row for each event that has none. balance_after is the
running balance from that replay.

An account is skipped when the replay does not end at its current
balance: its transactions don't explain its balance (it shows up in
account_balance_audit), so fix that first. Safe to run again: events that
already have a ledger row are left alone.
"""
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.database.session import SessionLocal
import app.main  # noqa: F401  (imports every model)
from app.routers.accounts import opening_reference
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.deposit import Deposit
from app.models.fee_record import FeeRecord
from app.models.interbank_transfer import InterbankTransfer
from app.models.interest_record import InterestRecord
from app.models.ledger_entry import LedgerEntry
from app.models.transfer import Transfer
from app.models.withdrawal import Withdrawal

ZERO = Decimal("0.00")
REFUNDED = ("FAILED", "REVERSED")


@dataclass
class Event:
    when: datetime
    order: int          # breaks ties: the opening deposit always comes first
    reference: str
    kind: str           # ledger_entries.transaction_type, as the routers write it
    debit: Decimal
    credit: Decimal


def events_for(db, account: Account) -> list[Event]:
    """Every balance change of one account, the way the routers record them."""
    events = []
    opening = db.query(AccountType.opening_deposit).filter(AccountType.id == account.account_type_id).scalar() or ZERO
    if opening:
        events.append(Event(account.opened_at, 0, opening_reference(account), "DEPOSIT", ZERO, opening))

    for d in db.query(Deposit).filter(Deposit.account_id == account.id, Deposit.status == "COMPLETED"):
        events.append(Event(d.transaction_date, 1, d.reference_number, "DEPOSIT", ZERO, d.amount))
    for w in db.query(Withdrawal).filter(Withdrawal.account_id == account.id):
        events.append(Event(w.transaction_date, 1, w.reference_number, "WITHDRAWAL", w.amount, ZERO))
    for t in db.query(Transfer).filter(Transfer.source_account_id == account.id):
        events.append(Event(t.completed_at or t.created_at, 1, t.transfer_reference, "TRANSFER_DEBIT", t.amount, ZERO))
    for t in db.query(Transfer).filter(Transfer.destination_account_id == account.id):
        events.append(Event(t.completed_at or t.created_at, 1, t.transfer_reference, "TRANSFER_CREDIT", ZERO, t.amount))
    for ib in db.query(InterbankTransfer).filter(InterbankTransfer.source_account_id == account.id):
        total = ib.amount + (ib.transfer_fee or ZERO)
        events.append(Event(ib.initiated_at, 1, ib.reference_number, "INTERBANK_DEBIT", total, ZERO))
        if ib.status in REFUNDED:
            events.append(Event(ib.completed_at or ib.initiated_at, 2, ib.reference_number, "REVERSAL", ZERO, total))
    for f in db.query(FeeRecord).filter(FeeRecord.account_id == account.id):
        events.append(Event(f.charged_at, 1, f.transaction_reference or f"FEE-{f.id}", "FEE", f.amount_charged, ZERO))
    for i in db.query(InterestRecord).filter(InterestRecord.account_id == account.id):
        events.append(Event(i.credited_at, 1, f"INT-{i.id}", "INTEREST", ZERO, i.amount_credited))

    events.sort(key=lambda e: (e.when or datetime.min, e.order))
    return events


def backfill(apply: bool) -> int:
    db = SessionLocal()
    written = 0
    try:
        for account in db.query(Account).order_by(Account.id):
            existing = Counter(
                (r.transaction_reference, r.transaction_type)
                for r in db.query(LedgerEntry).filter(LedgerEntry.account_id == account.id)
            )
            balance = ZERO
            missing = []
            for e in events_for(db, account):
                balance += e.credit - e.debit
                key = (e.reference, e.kind)
                if existing[key] > 0:
                    existing[key] -= 1  # this event already has its ledger row
                else:
                    missing.append((e, balance))

            if not missing:
                continue
            if balance != account.available_balance:
                print(f"SKIP {account.account_number}: transactions add up to {balance}, "
                      f"balance is {account.available_balance} (see account_balance_audit)")
                continue

            print(f"{account.account_number}: {len(missing)} ledger row(s) missing")
            for e, after in missing:
                print(f"    {e.when:%Y-%m-%d %H:%M}  {e.kind:<16} {e.reference:<32} "
                      f"-{e.debit:>10} +{e.credit:>10}  = {after}")
                db.add(LedgerEntry(
                    account_id=account.id,
                    transaction_reference=e.reference,
                    transaction_type=e.kind,
                    debit_amount=e.debit,
                    credit_amount=e.credit,
                    balance_after=after,
                    transaction_date=e.when,
                ))
                written += 1

        if apply:
            db.commit()
        else:
            db.rollback()
    finally:
        db.close()
    return written


if __name__ == "__main__":
    apply = "--apply" in sys.argv[1:]
    count = backfill(apply)
    if apply:
        print(f"Wrote {count} ledger row(s).")
    else:
        print(f"Dry run: {count} ledger row(s) would be written. Run with --apply to write them.")
