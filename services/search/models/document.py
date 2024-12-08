from pydantic import BaseModel
from typing import List, Union
from datetime import date


class Image(BaseModel):
    image_id: str
    image_embedding: list
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
    text_content_embedding: list
    metadata: Metadata
    images: List[Image]