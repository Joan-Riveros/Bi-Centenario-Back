from logging.config import fileConfig
from sqlalchemy import engine_from_config 
from sqlalchemy import pool 
from sqlalchemy import create_engine 
from alembic import context
from app.db.base import Base  # ← contiene todos tus modelos importados

import os
import sys
from dotenv import load_dotenv

# --- Configuración de Path y Carga de .env ---
# Esto añade la raíz del proyecto al sys.path para que se puedan importar los modulos de la app
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, '.env')) 
print("📦 Usando base de datos:", os.getenv("DATABASE_URL"))


# Es CRUCIAL que todos los modelos SQLAlchemy que Alembic debe gestionar
# sean importados ANTES de que se acceda a Base.metadata
from app.db.base import Base
from app.models.user import User
from app.models.forum import ForumCategory, ForumTopic, ForumPost
from app.models.notification import Notification 
from app.models.two_factor import User2FASetting


config = context.config


DATABASE_URL_FROM_ENV = os.getenv("DATABASE_URL")
if not DATABASE_URL_FROM_ENV:
    raise ValueError("DATABASE_URL no esta configurada en el archivo .env o no se pudo cargar")

config.set_main_option("sqlalchemy.url", DATABASE_URL_FROM_ENV)


# Base.metadata contendrs las definiciones de todas las tablas de los modelos importados.
target_metadata = Base.metadata


if config.config_file_name is not None:
    fileConfig(config.config_file_name)



def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'.
    Esto configura el contexto solo con una URL
    y no un Engine, aunque podría necesitar uno si se usan características específicas.
    Al generar SQL, esto emite las DDL al script.
    """
    url = config.get_main_option("sqlalchemy.url") 
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True, 
        dialect_opts={"paramstyle": "named"},
        # Considerar añadir include_object para ENUMs si hay problemas ojo
        # include_object=include_object_fn # (definir include_object_fn más arriba)
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'.
    En este escenario necesitamos crear un Engine
    y asociar una conexión con el contexto.
    """
    # La forma original de obtener el 'connectable' desde alembic.ini está comentada,
    # lo cual es correcto ya que estamos usando DATABASE_URL_FROM_ENV directamente.
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool, # NullPool es común para migraciones para evitar problemas de conexión
    # )

    # Crear el engine directamente usando la URL del .env
    connectable = create_engine(DATABASE_URL_FROM_ENV)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Opcional: funcion para manejar como se comparan/detectan ciertos tipos, como ENUMs.
            # Descomentar y ajustar si se tienen problemas con la autogeneracion de ENUMs.
            # def include_object(object, name, type_, reflected, compare_to):
            #     if type_ == "table" and object.meta.schema != target_metadata.schema:
            #         return False
            #     # Ejemplo para ENUMs (puede necesitar ajustes):
            #     # if type_ == "type" and reflected and object.name is None:
            #     # return False
            #     return True
            # include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()