from fastapi import APIRouter, Depends, Query, HTTPException

from models.abstract import PaginatedParams
from services.document import DocumentService, get_document_service
from core import config
from models.document import Document


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


@router.post("/add")
async def add_document(
    document: Document,
    document_service: DocumentService = Depends(get_document_service)
):
    response = await document_service.add_document(document)
    if "result" in response and response["result"] == "created":
        return {"message": "Document added successfully", "id": response["_id"]}
    raise HTTPException(status_code=500, detail="Failed to add document")
