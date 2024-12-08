import os
import numpy as np
from typing import List

from fastapi import (
    APIRouter, 
    Depends, 
    Query,
    UploadFile, 
    File,
    Request,
)
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image

from models.abstract import PaginatedParams
from models.document import Document
from services.document import DocumentService, get_document_service
from utils.file import save_file
from db.elastic import AsyncSearchService, get_elastic
from services.preprocessing import PreprocessingService, get_preprocessing_service
from core import config


router = APIRouter()


@router.post("/")
async def get_documents(
    query: str = Query(
        default='',
        strict=False,
        alias=config.QUERY_ALIAS,
        description=config.QUERY_DESC,
    ),
    pagination: PaginatedParams = Depends(),
    document_service: DocumentService = Depends(get_document_service)
):
    documents = await document_service.get_documents_by_query(
        query=query,
        page=pagination.page,
        size=pagination.size
    )

    return documents


@router.post("/multimodal_search")
async def get_documents_by_multimodal_query(
    query: str = Query(
        default='',
        strict=False,
        alias=config.QUERY_ALIAS,
        description=config.QUERY_DESC,
    ),
    image: UploadFile = None,
    pagination: PaginatedParams = Depends(),
    document_service: DocumentService = Depends(get_document_service),
    preprocessing_service: PreprocessingService = Depends(get_preprocessing_service),
):
    """
    Поиск документов с учетом текстового запроса и/или изображения.
    """
    query_vector = None
    image_vector = None

    # Обрабатываем текстовый запрос
    if query:
        query_vector = preprocessing_service.vectorize_text(query)

    # Обрабатываем изображение
    if image:
        temp_image_path = save_file(image, config.TEMP_FILES_DIR)
        try:
            image_obj = Image.open(temp_image_path)
            image_vector = preprocessing_service.vectorize_image(image_obj)
        finally:
            os.remove(temp_image_path)

    # Выполняем запрос в сервис поиска
    response = await document_service.get_documents_by_multimodal_query(
        query_vector=query_vector,
        image_vector=image_vector,
        page=pagination.page,
        size=pagination.size,
    )

    # Обработка результатов поиска
    hits = response["hits"]["hits"]
    if not hits:
        return {"message": "No documents found matching your query."}

    best_hit = hits[0]
    file_path = best_hit["_source"]["file_path"]

    # Возвращаем файл с наивысшим скором
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/octet-stream", filename=os.path.basename(file_path))
    else:
        return {"message": "Document found but file is missing on server."}


@router.get('/vectors/',
            response_model=List[List[float]],
            summary='Получить список всех векторов документов',
            description='Формат массива данных ответа: [[text_content_vector1], [text_content_vector2], [text_content_vector3], ...]')
async def documents_vectors(
        _: Request,
        film_service: DocumentService = Depends(get_document_service),
):
    vectors: List[List[float]] = await film_service.get_documents_vectors()

    return vectors


@router.post("/process/")
async def process_document_endpoint(
    file: UploadFile = File(...),
    preprocessing_service: PreprocessingService = Depends(get_preprocessing_service),
    search_service: AsyncSearchService = Depends(get_elastic)
):
    """
    Эндпоинт для загрузки документа и его обработки.
    """
    local_file_path = save_file(file, config.UPLOAD_FILES_DIR)
    
    result: Document = preprocessing_service.process_document(local_file_path)
    
    response = await search_service.index(index=config.document_index_name, body=result)
    
    new_file_path = os.path.join(config.UPLOAD_FILES_DIR, f"{response['_id']}{os.path.splitext(local_file_path)[-1]}")

    os.rename(local_file_path, new_file_path)
    
    result["file_path"] = new_file_path

    return JSONResponse(content=result)

