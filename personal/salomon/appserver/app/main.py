from fastapi import FastAPI
app = FastAPI()
@app.get("/",tags=["Root"], summary="Root endpoint")

def hello():
    return {"message": "Hello, World!"}
    
@app.get("/hello",tags= ["hello"], summary="Hello endpoint")
def hello_name():
    return {"message": "Hello from FastAPI!"}