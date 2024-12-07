from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError

from utils.abstract import AsyncSearchService

es: AsyncElasticsearch | None = None


class ElasticsearchAdapter(AsyncSearchService):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get(self, index: str, id: str, **kwargs):
        try:
            return await self.elastic.get(index=index, id=id, **kwargs)
        except (NotFoundError, BadRequestError):
            return None

    async def search(
        self,
        index: str,
        body: dict,
        **kwargs
    ):
        try:
            return await self.elastic.search(
                index=index, body=body,
                **kwargs
            )
        except (NotFoundError, BadRequestError):
            return None

    async def index(
        self,
        index: str,
        body: dict,
        id: str | None = None,
        **kwargs
    ):
        """
        Add or update a document in the Elasticsearch index.
        
        :param index: Name of the Elasticsearch index.
        :param body: The document to be indexed as a dictionary.
        :param id: Optional document ID. If not provided, Elasticsearch generates one.
        :param kwargs: Additional parameters for the Elasticsearch index method.
        :return: Response from Elasticsearch.
        """
        try:
            return await self.elastic.index(index=index, body=body, id=id, **kwargs)
        except BadRequestError as e:
            raise ValueError(f"Invalid indexing request: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to index document: {e}")


async def get_elastic() -> AsyncElasticsearch:
    return es
