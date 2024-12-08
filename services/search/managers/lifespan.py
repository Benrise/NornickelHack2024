import nltk

from elasticsearch import AsyncElasticsearch
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from transformers import ViTModel, ViTImageProcessor


from utils.logger import logger
from services import preprocessing


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

    async def upload_preprocessing_models(self):
        logger.info("Loading preprocessing models...")
        logger.info("Loading VIT model...")
        preprocessing.VIT_MODEL = ViTModel.from_pretrained(
            "google/vit-base-patch16-224-in21k"
        )
        preprocessing.VIT_PROCESSOR = ViTImageProcessor.from_pretrained(
            "google/vit-base-patch16-224-in21k"
        )
        logger.info("Loading vectorizer...")
        preprocessing.VECTORIZER_MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("Finding stopwords...")
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading stopwords...")
            nltk.download('stopwords')
        preprocessing.STOPWORD_COLLECTION = set(stopwords.words('russian'))
        logger.info("Downloading punkt...")
        nltk.download('punkt')
        logger.info("Uploading preprocessing models complete.")