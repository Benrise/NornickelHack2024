import os
import shutil
from typing import List

from fastapi import (
    APIRouter, 
    Depends, 
    Query, 
    HTTPException, 
    UploadFile, 
    File,
    Request
)
from fastapi.responses import JSONResponse

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
    
    try:
        result: Document = preprocessing_service.process_document(local_file_path)
        
        #os.remove(local_file_path)
        
        await search_service.index(index=config.document_index_name, body=result)

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

