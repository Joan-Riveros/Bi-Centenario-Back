from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user as user_public_router
from app.routes import admin_users as admin_users_router
from app.routes import forum
from app.routes import notification
from app.core.init_admin import create_default_admin  # 👈 IMPORTANTE

app = FastAPI(
    title="Repositorio de Documentos Históricos Digitalizados",
    description="API para la gestión y acceso a documentos históricos digitalizados",
    version="0.1.0",
)

# Middleware CORS (opcional si tienes frontend separado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes reemplazar "*" por tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejecutar al iniciar el backend
@app.on_event("startup")
def startup_event():
    create_default_admin()

# Ruta raíz
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenido a la API del Repositorio de Documentos Históricos Digitalizados"}

# Rutas
app.include_router(
    user_public_router.router,
    prefix="/users",
    tags=["Usuarios - Autenticación y perfil público"]
)

app.include_router(
    admin_users_router.router,
    prefix="/admin/users",
    tags=["Administración - Usuarios"]
)

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
