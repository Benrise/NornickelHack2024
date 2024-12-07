from pydantic import BaseModel
from typing import List, Union
from datetime import date


class ImageOCR(BaseModel):
    image_id: str
    ocr_text: str
    position: str
    image_path: str


class Metadata(BaseModel):
    author: Union[str, None]
    created_date: date
    tags: List[str]


class Document(BaseModel):
    document_id: str
    title: str
    text_content: str
    metadata: Metadata
    images: List[ImageOCR]