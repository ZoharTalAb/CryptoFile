from fastapi import FastAPI
from presentation.routes import auth_routes

app = FastAPI()

app.include_router(auth_routes.router)

from presentation.routes import user_routes

app.include_router(user_routes.router)
