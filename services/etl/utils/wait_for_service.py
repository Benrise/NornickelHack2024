import time

import requests

from .logger import logger


def wait_for_service(url, retries=90, delay=3):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.info(f"Service at {url} is available.")
                return
        except requests.exceptions.ConnectionError:
            pass
        logger.info(f"Waiting for {url}... ({attempt + 1}/{retries})")
        time.sleep(delay)
    raise RuntimeError(f"Service at {url} is not available after {retries * delay} seconds.")
