from fastapi import FastAPI
from app.routes import user as user_public_router 
from app.routes import admin_users as admin_users_router 
from app.routes import forum
from app.routes import notification
app = FastAPI(
    title="Repositorio de Documentos Historicos Digitalizados",
    description="API para la gestion y acceso a documentos historicos digitalizados",
    version="0.1.0", 
    # metadatos API
)

# Registro de routers:
app.include_router(
    user_public_router.router, 
    prefix="/users",
    tags=["Usuarios - Autenticacion y perfil publico"] 
)
app.include_router(
    admin_users_router.router, 
    prefix="/admin/users", 
    tags=["Administracion - Usuarios"] 
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenido a la API del Repositorio de Documentos Historicos Digitalizados"}

# 
app.include_router(
    forum.router,
    prefix="/forum",
    tags=["Foro"]
)

app.include_router(
    notification.router,
    prefix="/forum",
    tags=["Notificaciones"]
)