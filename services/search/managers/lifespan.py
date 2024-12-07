
from elasticsearch import AsyncElasticsearch

from utils.logger import logger


class LifespanManager:
    def __init__(self, es_conn: AsyncElasticsearch):
        self.es = es_conn

    async def init_es(
        self,
        indicies: list[str]
    ):
        async def check_connection(self=self):
            try:
                health = await self.es.cluster.health()
                logger.info(f"Elasticsearch connection successful: {health}")
            except Exception as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}")
                raise

        async def ensure_index_exists(
            name: str,
            body: dict,
            self=self,
        ):
            try:
                exists = await self.es.indices.exists(index=name)
                if not exists:
                    await self.es.indices.create(
                        index=name, body=body
                    )
                    logger.info(f"Index '{name}' created successfully.")
                else:
                    logger.info(f"Index '{name}' already exists.")
            except Exception as e:
                logger.error(f"Failed to create or check index: {e}")
                raise

        await check_connection()

        for index in indicies:
            await ensure_index_exists(name=index["name"], body=index["body"])
