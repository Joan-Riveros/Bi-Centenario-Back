from routes import user
from db.base import Base
from db.session import engine
from fastapi import FastAPI
from routes import auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/users", tags=["Usuarios"])
app.include_router(auth.router, tags=["Auth"])
