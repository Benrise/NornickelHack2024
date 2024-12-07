from fastapi import APIRouter, Depends, Query

from models.abstract import PaginatedParams
from services.document import DocumentService, get_document_service
from core import config


router = APIRouter()


@router.post("/")
async def get_documents(
    query: str = Query(
        default='Машиностроение',
        strict=True,
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
