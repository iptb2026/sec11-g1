from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.core.audit  # noqa: F401  (turns on automatic audit logging)
from app.core.config import settings
from app.core.security import ADMIN_AUDITOR, ADMIN_ONLY, ADMIN_STAFF, ALL_ROLES, STAFF_READERS, allow_roles
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# ==== LAYER 2: Identity & Access ====
from app.routers import users, auth, sessions, audit_logs

# ==== LAYER 3: Account Configuration ====
from app.routers import accounts, withdrawal_limits, interest_policies

# ==== LAYER 4: Transactions ====
from app.routers import deposits, withdrawals, transfers, interbank_transfers

# ==== LAYER 5: Financial Records & Ledger ====
from app.routers import fee_records, interest_records, ledger_entries

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Allows the Quasar frontend (a different origin/port, e.g. http://localhost:9000)
# to call this API from the browser. Wide open here since this is a learning
# project with no real users; a production app would restrict allow_origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Every router except /auth requires a logged-in user with the right role
# (see allow_roles in core/security.py). /auth stays open so people can log in.
#   read  = roles allowed to GET, write = roles allowed to POST/PUT/DELETE
# Routers that customers can read also filter rows to the customer's own
# accounts, and /users checks "own profile" itself (see those routers).
# AUDITOR can read everything except login sessions (they hold tokens) and
# can write nothing.
admin_only = [allow_roles(read=ADMIN_ONLY, write=ADMIN_ONLY)]
audit_trail = [allow_roles(read=ADMIN_AUDITOR, write=())]
reference_data = [allow_roles(read=STAFF_READERS, write=ADMIN_ONLY)]
staff_work = [allow_roles(read=STAFF_READERS, write=ADMIN_STAFF)]
customer_readable = [allow_roles(read=ALL_ROLES, write=ADMIN_STAFF)]
users_policy = [allow_roles(read=ALL_ROLES, write=("ADMIN", "STAFF", "CUSTOMER"))]

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router, dependencies=reference_data)
app.include_router(account_types.router, dependencies=reference_data)
app.include_router(banks.router, dependencies=reference_data)
app.include_router(fee_types.router, dependencies=reference_data)

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router, dependencies=users_policy)
app.include_router(auth.router)
app.include_router(sessions.router, dependencies=admin_only)
app.include_router(audit_logs.router, dependencies=audit_trail)

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router, dependencies=customer_readable)
app.include_router(withdrawal_limits.router, dependencies=staff_work)
app.include_router(interest_policies.router, dependencies=staff_work)

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router, dependencies=customer_readable)
app.include_router(withdrawals.router, dependencies=customer_readable)
app.include_router(transfers.router, dependencies=customer_readable)
app.include_router(interbank_transfers.router, dependencies=customer_readable)

# ==== LAYER 5: Financial Records & Ledger ====
app.include_router(fee_records.router, dependencies=customer_readable)
app.include_router(interest_records.router, dependencies=customer_readable)
app.include_router(ledger_entries.router, dependencies=customer_readable)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/hello", tags=["Health"], summary="Hello endpoint")
def hello():
    return {"message": "Hello from Banking System API!"}