from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=[""], # Allow all origins
allow_credentials=False, # Set to True only if using cookies/auth
allow_methods=[""], # Allow all HTTP methods
allow_headers=["*"], # Allow all headers
)

@app.get("/", tags=["Root"], summary="Root endpoint")
def hello():
return {"message": "Hello, World!"}

@app.get("/hello", tags=["Hello"], summary="Hello endpoint")
def hello_name():
return {"message": "Hello from FastAPI!"}