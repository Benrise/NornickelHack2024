import os
import shutil
from fastapi import UploadFile

def save_file(file: UploadFile, upload_dir: str) -> str:
    ext = os.path.splitext(file.filename)[-1].lower()
    
    os.makedirs(upload_dir, exist_ok=True)
    
    local_file_path = os.path.join(upload_dir, file.filename)
    
    with open(local_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return local_file_path