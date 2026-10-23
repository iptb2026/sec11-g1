from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import get_current_user
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

# Every router except /auth requires a logged-in user (see get_current_user).
# /auth stays open so people can log in; /auth/logout checks its own token.
login_required = [Depends(get_current_user)]

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router, dependencies=login_required)
app.include_router(account_types.router, dependencies=login_required)
app.include_router(banks.router, dependencies=login_required)
app.include_router(fee_types.router, dependencies=login_required)

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router, dependencies=login_required)
app.include_router(auth.router)
app.include_router(sessions.router, dependencies=login_required)
app.include_router(audit_logs.router, dependencies=login_required)

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router, dependencies=login_required)
app.include_router(withdrawal_limits.router, dependencies=login_required)
app.include_router(interest_policies.router, dependencies=login_required)

# ==== LAYER 4: Transactions ====
app.include_router(deposits.router, dependencies=login_required)
app.include_router(withdrawals.router, dependencies=login_required)
app.include_router(transfers.router, dependencies=login_required)
app.include_router(interbank_transfers.router, dependencies=login_required)

# ==== LAYER 5: Financial Records & Ledger ====
app.include_router(fee_records.router, dependencies=login_required)
app.include_router(interest_records.router, dependencies=login_required)
app.include_router(ledger_entries.router, dependencies=login_required)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/hello", tags=["Health"], summary="Hello endpoint")
def hello():
    return {"message": "Hello from Banking System API!"}