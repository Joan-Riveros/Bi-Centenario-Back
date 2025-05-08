from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import os
import sys
from dotenv import load_dotenv



PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, '.env')) # Cargar .env desde el directorio raiz


from app.db.base import Base  
from app.models.user import User # Importa tu modelo User
# Importar abajo otros modelos
# from app.models.otro_modelo import OtroModelo

# Configuración de Alembic
config = context.config


DATABASE_URL_FROM_ENV = os.getenv("DATABASE_URL")
if not DATABASE_URL_FROM_ENV:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env o no se pudo cargar.")
config.set_main_option("sqlalchemy.url", DATABASE_URL_FROM_ENV)

# Establece target_metadata para el soporte de 'autogenerate'
target_metadata = Base.metadata



if config.config_file_name is not None:
    fileConfig(config.config_file_name)



def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'.
    # ... (contenido existente) ...
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata, 
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'.
    # ... (contenido existente) ...
    """
    # Reemplaza la forma en que se crea 'connectable' para usar directamente tu DATABASE_URL
    # connectable = engine_from_config(  # <--- Línea original a comentar o reemplazar
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

   
    from sqlalchemy import create_engine
    connectable = create_engine(DATABASE_URL_FROM_ENV) # Usar la URL cargada anteriormente
    

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata 
            # Descomenta la siguiente linea si usas Enums de SQLAlchemy y tienes problemas con su generación
            # include_object=lambda obj, name, type_, reflected, compare_to: \
            #     not (type_ == "type" and reflected and obj.name is None)
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()