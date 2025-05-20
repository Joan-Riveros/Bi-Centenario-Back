from fastapi import FastAPI
from app.routes import user as user_public_router 
from app.routes import admin_users as admin_users_router 
from app.routes import forum
from app.routes import notification
from app.routes import documents
#documents
from app.utils.file_system import ensure_upload_dirs_exist
from app.routes import admin_management, researcher_requests, document_proposals
#
#FRONTEND
from fastapi.middleware.cors import CORSMiddleware
#
app = FastAPI(
    title="Repositorio de Documentos Historicos Digitalizados",
    description="API para la gestion y acceso a documentos historicos digitalizados",
    version="0.1.0", 
    
)


ensure_upload_dirs_exist()
origins = [
    "http://localhost",         
    "http://localhost:3000",    
    "http://localhost:5173",    
    
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"],
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

#documents
app.include_router(
    admin_management.router,
    prefix="/admi",
    tags=["Admin Management"], 

)


app.include_router(
    researcher_requests.router,
    prefix="/researcher",
    tags=["Researcher Requests"])

app.include_router( 
    document_proposals.router,
    prefix="/document-proposals", 
    tags=["Document Proposals (Uploads)"],
)

app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents (General Access & Download)"]
)
