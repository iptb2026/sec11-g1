from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import Base, engine
from app.routers import roles, account_types, banks, fee_types

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router)
app.include_router(account_types.router)
app.include_router(banks.router)
app.include_router(fee_types.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/", tags=["Root"], summary="Root endpoint")
def hello():
    return {"message": "Hello, World!"}


@app.get("/hello", tags=["Hello"], summary="Hello endpoint")
def hello_name():
    return {"message": "Hello from FastAPI!"}