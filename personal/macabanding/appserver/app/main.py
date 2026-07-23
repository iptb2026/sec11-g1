from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def greet():
    return{"message" : "Hello Mom :3"}

@app.get("/greet")
def greet_name():
    return {"message": "Hello from FastAPI :>"}