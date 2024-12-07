import os
from typing import List, Dict, Union
from logging import config as logging_config
from libs.es.indices.document import (
    index_name as document_index_name,
    index_json as document_index_json
)

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QUERY_DESC = "Поисковая строка"
QUERY_ALIAS = "query"

PAGE_DESC = "Номер страницы"
PAGE_ALIAS = "page"

SIZE_DESC = "Количество элементов на странице"
SIZE_ALIAS = "size"

MAX_PAGE_SIZE = 100
MAX_GENRES_SIZE = 50


logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field(..., alias='SEARCH_SERVICE_PROJECT_NAME')
    service_host: str = Field('content', alias='SEARCH_SERVICE_HOST')
    service_port: int = Field(8000, alias='SEARCH_SERVICE_PORT')


settings = Settings()


class ElasticsearchSettings(BaseSettings):
    es_protocol: str = Field('http', alias='SEARCH_ES_PROTOCOL')
    es_host: str = Field('elasticsearch', alias='SEARCH_ES_HOST')
    es_port: int = Field(9200, alias='SEARCH_ES_PORT')
    indicies: List[Dict[str, Union[str, dict]]] = [
        {
            "name": document_index_name,
            "body": document_index_json
        }
    ]

    @property
    def elastic_url(self):
        return f'{self.es_protocol}://{self.es_host}:{self.es_port}'


es_settings = ElasticsearchSettings()
