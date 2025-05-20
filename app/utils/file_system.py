import os
from pathlib import Path
from app.core.config import UPLOAD_DOCUMENTS_DIR, UPLOAD_COVERS_DIR

def ensure_upload_dirs_exist():
    Path(UPLOAD_DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(UPLOAD_COVERS_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Upload directories ensured: {UPLOAD_DOCUMENTS_DIR}, {UPLOAD_COVERS_DIR}")