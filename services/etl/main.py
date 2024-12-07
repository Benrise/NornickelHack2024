import os

from elasticsearch import Elasticsearch
from services.lodaer import ElasticLoader
from utils.logger import logger
from utils.wait_for_service import wait_for_service
from libs.es.indices.document import index_name, index_json

ELASTIC_PROTOCOL = os.getenv('ELASTICSEARCH_PROTOCOL', 'http')
ELASTIC_HOST = os.getenv('ELASTICSEARCH_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))

HOSTS = [f"{ELASTIC_PROTOCOL}://{ELASTIC_HOST}:{ELASTIC_PORT}"]

FILE_PATH = "./data/output.json"

hosts = [f'{ELASTIC_PROTOCOL}://{ELASTIC_HOST}:{ELASTIC_PORT}']


if __name__ == "__main__":
    client = Elasticsearch(hosts=hosts)
    loader = ElasticLoader(client)

    wait_for_service(f'{ELASTIC_PROTOCOL}://{ELASTIC_HOST}:{ELASTIC_PORT}')

    if not client.indices.exists(index=index_name):
        logger.info(f"Index {index_name} does not exist. Creating...")
        client.indices.create(index=index_name, body=index_json)

    logger.info(f"Loading documents from {FILE_PATH} into {index_name}...")
    loader.load_documents_from_file(index=index_name, file_path=FILE_PATH)
