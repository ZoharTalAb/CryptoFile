from fastapi import FastAPI
from presentation.routes import auth_routes, user_routes, stego_routes
from infrastructure.db.session import engine
from infrastructure.db.models import Base

app = FastAPI(
    title="CryptoFile API",
    description="מערכת להעברת הודעות מאובטחת באמצעות סטגנוגרפיה בתמונות, אודיו וטקסט",
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)

# רישום ה-Routers של המערכת
app.include_router(auth_routes.router)
app.include_router(user_routes.router)

# כאן אנחנו מחברים את הנתיב החדש שיצרת!
app.include_router(stego_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to CryptoFile API - Steganography Engine is Ready!"}
