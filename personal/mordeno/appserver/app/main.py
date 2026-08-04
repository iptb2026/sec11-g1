from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)

@app.get("/",tags=["Root"], summary="Root endpoint")
def hello():
    return {"message": "Hello, World!"}

@app.get("/hello",tags=["hello"], summary="Hello enpoint")
def hello_name():
    return {"message": "Hello from FastAPI!"}

