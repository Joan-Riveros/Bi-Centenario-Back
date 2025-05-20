import shutil
import uuid
from pathlib import Path 
from typing import Set
import os 
from fastapi import UploadFile, HTTPException, status

def save_upload_file(
    *,
    upload_file: UploadFile,
    destination_dir: Path, 
    max_size_mb: int,
    allowed_extensions: Set[str]
) -> str:
    """
    Guarda un UploadFile, verifica tipo y tamaño, y devuelve la ruta relativa
    """
    # Verificar tamaño
    upload_file.file.seek(0, 2)
    size_bytes = upload_file.file.tell() 
    upload_file.file.seek(0) 
    if size_bytes > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el tamaño maximo de {max_size_mb}MB.",
        )

    # Verificar extensión
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo no proporcionado",
        )
    file_extension = Path(upload_file.filename).suffix.lower() 
    if not file_extension: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene extension",
        )
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido Permitidos: {', '.join(allowed_extensions)}",
        )

    # Crear nombre 
    unique_filename_stem = str(uuid.uuid4()) 
    unique_filename = f"{unique_filename_stem}{file_extension}" 
    
    # destination_path = os.path.join(destination_dir, unique_filename)
    # Si destination_dir ES un objeto Path

    destination_dir.mkdir(parents=True, exist_ok=True) 

    destination_path_obj = destination_dir / unique_filename 

    try:
        with open(destination_path_obj, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except IOError as e: 

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo guardar el archivo debido a un error del servidor: {e}",
        )
    finally:
        upload_file.file.close()
    
    try:
        relative_path = destination_path_obj.relative_to(destination_dir.parent)
        return str(relative_path)
    except ValueError as e:
      
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al calcular la ruta del archivo guardado.",
        )