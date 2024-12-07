from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from utils.abstract import AsyncSearchService
from db.elastic import get_elastic, ElasticsearchAdapter


async def get_search_service(
    elastic: AsyncElasticsearch = Depends(get_elastic)
) -> AsyncSearchService:
    return ElasticsearchAdapter(elastic)
