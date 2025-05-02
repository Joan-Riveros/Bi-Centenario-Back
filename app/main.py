from fastapi import FastAPI
from app.routes import user
from app.db.base import Base
from app.db.session import engine

app = FastAPI()

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Registrar rutas
app.include_router(user.router, prefix="/users", tags=["Usuarios"])
