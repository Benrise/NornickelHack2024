from pydantic import BaseModel
from typing import List
from datetime import date


class ImageOCR(BaseModel):
    image_id: str
    ocr_text: str
    position: str
    image_path: str


class Metadata(BaseModel):
    file_type: str
    author: str
    created_date: date
    tags: List[str]


class Document(BaseModel):
    doc_id: str
    title: str
    text_content: str
    metadata: Metadata
    images: List[ImageOCR]