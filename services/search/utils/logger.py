import uuid
import json
import os
import logging
from logging.handlers import RotatingFileHandler
from core.config import settings

LOGS_DIR = './logs'

os.makedirs(LOGS_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', uuid.uuid4().hex),
            'host': getattr(record, 'host', settings.service_host),
            'method': getattr(record, 'method', None),
            'query_params': getattr(record, 'query_params', None),
            'status_code': getattr(record, 'status_code', None),
            'elapsed_time': getattr(record, 'elapsed_time', None)
        }

        return json.dumps(log_message)


app_name = 'search'

log_file = os.path.join(LOGS_DIR, "logs.log")
max_bytes = 10 * 1024 * 1024
backup_count = 5

logger = logging.getLogger(app_name)
logger.setLevel(logging.INFO)

formatter = JsonFormatter()

rotating_file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
rotating_file_handler.setFormatter(formatter)
rotating_file_handler.setLevel(logging.INFO)

logger.addHandler(rotating_file_handler)
