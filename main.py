from fastapi import FastAPI
from app.routes import user as user_public_router 
from app.routes import admin_users as admin_users_router 

app = FastAPI(
    title="Repositorio de Documentos Historicos Digitalizados",
    description="API para la gestión y acceso a documentos históricos digitalizados.",
    version="0.1.0", 
    # metadatos API
)

# Registro de routers:
app.include_router(
    user_public_router.router, 
    prefix="/users",
    tags=["Usuarios - Autenticación y Perfil Publico"] 
)
app.include_router(
    admin_users_router.router, 
    prefix="/admin/users", 
    tags=["Administración - Usuarios"] 
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenido a la API del Repositorio de Documentos Historicos Digitalizados"}