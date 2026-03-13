from fastapi import FastAPI
from app.routers import auth, plants, users

app = FastAPI(title="Plant Care API", version="1.0.0")
app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(users.router)

