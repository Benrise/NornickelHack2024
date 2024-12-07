import uvicorn
import logging

from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.responses import ORJSONResponse
from elasticsearch import AsyncElasticsearch

from db import elastic

from core.config import settings, es_settings
from core.logger import LOGGING
from utils.logger import logger
from managers.lifespan import LifespanManager


@asynccontextmanager
async def lifespan(_: FastAPI):
    elastic.es = AsyncElasticsearch(hosts=[es_settings.elastic_url])
    lifespan_manager = LifespanManager(elastic.es)
    await lifespan_manager.init_es(indicies=es_settings.indicies)
    yield
    await elastic.es.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/search/api/v1/docs',
    openapi_url='/search/api/v1/docs.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()

    logger.info(
        "middleware",
        extra={
            "request_id": None,
            "host": settings.service_host,
            "method": request.method,
            "query_params": str(request.query_params),
            "status_code": response.status_code,
            "elapsed_time": (end_time - start_time).total_seconds(),
        }
    )

    return response


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=settings.service_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
