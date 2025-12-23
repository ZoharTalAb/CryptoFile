from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "CryptoFile backend is running"}


# Temporary change to force git to track backend
