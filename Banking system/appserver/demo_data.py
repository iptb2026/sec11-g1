"""
Create realistic demo data THROUGH THE API, so every balance, ledger row
and audit log is made exactly the way the app makes them.

Start the backend first, then run from Banking system/appserver:

    .\\virt\\Scripts\\python demo_data.py --password <admin password>
    .\\virt\\Scripts\\python demo_data.py --api http://127.0.0.1:8000/catarig --password ...

It logs in as an ADMIN (default user: admin) and creates, if they don't
exist yet: two customers with a savings account each, then deposits, a
withdrawal, a transfer between them and an interbank transfer to BDO
marked SUCCESS. Customer passwords are `password123`.

Run it once on a clean database (see reset_transactions.sql). Running it
again adds another round of transactions, with new reference numbers.
Needs seed.py to have run (roles, SAVINGS, BDO). Uses only the standard
library, so no extra install.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

CUSTOMER_PASSWORD = "password123"

# (username, first, last, email, opening deposits)
CUSTOMERS = [
    ("lmercado", "Liza", "Mercado", "lmercado@minibank.com", [15000, 2500]),
    ("preyes", "Pedro", "Reyes", "preyes@minibank.com", [8000]),
]


class Api:
    def __init__(self, base: str):
        self.base = base.rstrip("/")
        self.token = None

    def call(self, method: str, path: str, body=None, form=False):
        data = None
        headers = {}
        if body is not None:
            if form:
                data = urllib.parse.urlencode(body).encode()
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                data = json.dumps(body).encode()
                headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                text = resp.read().decode()
                return json.loads(text) if text else None
        except urllib.error.HTTPError as err:
            sys.exit(f"{method} {path} failed with {err.code}: {err.read().decode()}")
        except urllib.error.URLError as err:
            sys.exit(f"Can't reach the API at {self.base} ({err.reason}). Is the backend running?")

    def login(self, username: str, password: str):
        data = self.call("POST", "/auth/login", {"username": username, "password": password}, form=True)
        self.token = data["access_token"]


def by(rows, field, value):
    return next((r for r in rows if r[field] == value), None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create demo data through the API.")
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="backend base URL")
    parser.add_argument("--user", default="admin", help="an ADMIN username")
    parser.add_argument("--password", required=True, help="that user's password")
    args = parser.parse_args()

    api = Api(args.api)
    api.login(args.user, args.password)
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")

    roles = api.call("GET", "/roles/")
    customer_role = by(roles, "role_code", "CUSTOMER")
    savings = by(api.call("GET", "/account-types/"), "type_code", "SAVINGS")
    bdo = by(api.call("GET", "/banks/"), "bank_code", "BDO")
    if not (customer_role and savings and bdo):
        sys.exit("Run seed.py first: the CUSTOMER role, SAVINGS account type and BDO bank are needed.")

    users = api.call("GET", "/users/")
    accounts = api.call("GET", "/accounts/")
    account_ids = []
    for username, first, last, email, deposits in CUSTOMERS:
        user = by(users, "username", username)
        if not user:
            user = api.call("POST", "/users/", {
                "username": username, "password": CUSTOMER_PASSWORD, "email": email,
                "first_name": first, "last_name": last, "role_id": customer_role["id"],
            })
            print(f"Created customer {username}")
        account = by(accounts, "customer_id", user["id"])
        if not account:
            account = api.call("POST", "/accounts/", {"customer_id": user["id"], "account_type_id": savings["id"]})
            print(f"Opened account {account['account_number']} for {username}")
        account_ids.append(account["id"])
        for n, amount in enumerate(deposits, 1):
            api.call("POST", "/deposits/", {
                "account_id": account["id"], "reference_number": f"DEP-{stamp}-{username}-{n}",
                "amount": amount, "deposit_channel": "CASH", "remarks": "Demo deposit",
            })
        print(f"  {len(deposits)} deposit(s) for {username}")

    liza, pedro = account_ids
    api.call("POST", "/withdrawals/", {
        "account_id": liza, "reference_number": f"WDR-{stamp}-1", "amount": 1500,
        "withdrawal_channel": "ATM", "remarks": "Demo ATM withdrawal",
    })
    api.call("POST", "/transfers/", {
        "source_account_id": liza, "destination_account_id": pedro,
        "transfer_reference": f"TRF-{stamp}-1", "amount": 3000, "remarks": "Demo transfer",
    })
    interbank = api.call("POST", "/interbank-transfers/", {
        "source_account_id": pedro, "target_bank_id": bdo["id"], "target_account_number": "001234567890",
        "beneficiary_name": "Ana Cruz", "reference_number": f"IBT-{stamp}-1", "amount": 2000, "transfer_fee": 25,
    })
    api.call("PUT", f"/interbank-transfers/{interbank['id']}/status", {"status": "SUCCESS"})
    print("Added a withdrawal, a transfer and an interbank transfer (SUCCESS).")

    for acc in api.call("GET", "/accounts/"):
        if acc["id"] in account_ids:
            print(f"  {acc['account_number']}: balance {acc['available_balance']}")


if __name__ == "__main__":
    main()
