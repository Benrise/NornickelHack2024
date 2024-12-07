from typing import List, Union

from functools import lru_cache
from fastapi import Depends

from utils.abstract import AsyncSearchService
from models.document import Document
from libs.es.indices.document import index_name
from dependencies.search import get_search_service


class DocumentService:
    def __init__(self, search_service: AsyncSearchService):
        self.search_service = search_service

    async def get_documents_by_query(
        self,
        query: str,
        page: int,
        size: int
    ) -> List[Union[Document, None]]:
        page -= 1
        body = {
            "from": page,
            "size": size,
            "query": {"match": {"title": {"query": query}}}
        }
        doc = await self.search_service.search(
            index=index_name,
            body=body,
            _source_includes=[
                "title",
                "text_content",
                "metadata.author",
                "metadata.created_date"
            ]
        )

        return [Document(**i['_source']) for i in doc['hits']['hits']]


@lru_cache()
def get_document_service(
        search_service: AsyncSearchService = Depends(get_search_service),
) -> DocumentService:
    return DocumentService(search_service)
