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
        }
        
        if len(query) == 0 or query is None:
            body["query"] = {"match_all": {}}
        else:
            body["query"] = {"match": {"title": {"query": query}}}
        
        doc = await self.search_service.search(
            index=index_name,
            body=body,
            _source_includes=None
        )

        return [Document(**i['_source']) for i in doc['hits']['hits']]

    async def add_document(self, document: Document) -> dict:
        response = await self.search_service.index(
            index=index_name,
            body=document.model_dump(),
        )
        return response
    
    async def get_documents_vectors(self) -> List[List[float]]:
        vectors = []
        size = 100
        from_ = 0
        while True:
            body = {
                "from": from_,
                "size": size,
                "_source": ["text_content_embedding"],
                "query": {
                    "match_all": {}
                }
            }
            response = await self.search_service.search(
                index=index_name,
                body=body,
                _source_includes=["text_content_embedding"]
            )

            hits = response['hits']['hits']
            if not hits:
                break

            vectors.extend(hit["_source"]["text_content_embedding"] for hit in hits)
            from_ += size

        return vectors


@lru_cache()
def get_document_service(
        search_service: AsyncSearchService = Depends(get_search_service),
) -> DocumentService:
    return DocumentService(search_service)
