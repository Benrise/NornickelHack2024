import os
from typing import List, Union

from functools import lru_cache
from fastapi import Depends
from fastapi.responses import FileResponse


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
        
        if not query:
            body["query"] = {"match_all": {}}
        else:
            body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "text_content"],
                }
            }
        
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


    async def get_documents_by_multimodal_query(
        self,
        query_vector: List[float],  # Вектор текста
        image_vector: List[float],  # Вектор изображения
        page: int,
        size: int,
    ) -> dict:
        """
        Выполняет мультимодальный поиск по вектору изображения и текстовому вектору.
        """
        # Проверяем наличие векторов
        if not image_vector and not query_vector:
            return {"message": "No image or query vector provided for the search."}

        # Строим тело запроса
        body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}  # Ищем все документы
                    },
                    "script": {
                        "source": """
                            double image_score = 0.0;
                            double text_score = 0.0;

                            // Проверяем, есть ли вектор изображения
                            if (params.image_vector != null && doc['image_embedding'].size() > 0) {
                                image_score = cosineSimilarity(params.image_vector, doc['image_embedding']) + 1.0;
                            }

                            // Проверяем, есть ли текстовый вектор
                            if (params.query_vector != null && doc['text_content_embedding'].size() > 0) {
                                text_score = cosineSimilarity(params.query_vector, doc['text_content_embedding']) + 1.0;
                            }

                            // Суммируем оценки
                            return image_score + text_score;
                        """,
                        "params": {
                            "image_vector": image_vector,
                            "query_vector": query_vector
                        }
                    }
                }
            },
            "from": (page - 1) * size,
            "size": size,
        }

        # Выполняем запрос в Elasticsearch
        response = await self.search_service.search(
            index=index_name,
            body=body,
            _source_includes=["document_id", "image_embedding", "text_content_embedding"]
        )

        # Проверка на None в случае ошибки Elasticsearch
        if response is None or response["hits"] is None:
            return {"message": "No documents found or error in search."}

        # Обработка успешного ответа
        hits = response["hits"]["hits"]
        if not hits:
            return {"message": "No documents found matching your query."}

        best_hit = hits[0]
        document_id = best_hit["_source"]["document_id"]
        image_embedding = best_hit["_source"]["image_embedding"]

        # Возвращаем лучший результат
        return {"document_id": document_id, "image_embedding": image_embedding}



@lru_cache()
def get_document_service(
        search_service: AsyncSearchService = Depends(get_search_service),
) -> DocumentService:
    return DocumentService(search_service)
