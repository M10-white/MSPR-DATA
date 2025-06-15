from fastapi import FastAPI

app = FastAPI(title="Minimal Test API")
 
@app.get("/")
def read_root():
    return {"message": "Hello from Minimal Test API"} 