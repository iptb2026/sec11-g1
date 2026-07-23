from fastapi import FastAPI
app = FastAPI()

@app.get("/", tags=["Root"], summary="Root Endpoint")
def greet():
    return{"message" : "Hello Mom :3"}

@app.get("/greet", tags=["Greet"], summary="Greeting Endpoint")
def greet_name():
    return {"message": "Hello from FastAPI :>"}
