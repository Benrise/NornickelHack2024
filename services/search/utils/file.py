import os
import shutil
from fastapi import HTTPException, UploadFile

def save_file(file: UploadFile, upload_dir: str) -> str:
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only .pdf and .docx are allowed.")
    
    os.makedirs(upload_dir, exist_ok=True)
    
    local_file_path = os.path.join(upload_dir, file.filename)
    
    with open(local_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return local_file_path