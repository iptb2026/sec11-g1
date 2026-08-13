from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (Development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all websites
    allow_credentials=False,
    allow_methods=["*"],        # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Allow all headers
)


@app.get("/",tags=["Root"], summary="Root endpoint")
def hello():
    return{"message": "Hello, World!"}


@app.get("/hello",tags=["hello"], summary="Hello endpoint")
def hello_name():
    return{"message": "Hello from FastAPI!"}