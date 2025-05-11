from fastapi import FastAPI
from app.routes import user
from app.db.base import Base
from app.db.session import engine
from app.routes import forum
from app.core.init_admin import create_default_admin
from app.routes import notification
from app.routes import admin_users
app = FastAPI()

# Crear las tablas
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    create_default_admin()
    
# Registrar rutas
app.include_router(user.router, prefix="/users", tags=["Usuarios"])

app.include_router(forum.router, prefix="/forum", tags=["Foro"])

app.include_router(notification.router, prefix="/forum", tags=["Notificaciones"])
app.include_router(admin_users.router, prefix="/admin/users", tags=["Admin Users"])