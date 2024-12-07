import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

logs_dir = "./logs"
os.makedirs(logs_dir, exist_ok=True)

app_name = 'etl'
timestamp = datetime.now().strftime("%d-%m-%Y")
main_log_file = os.path.join(logs_dir, f"{timestamp}_info.log")
error_log_file = os.path.join(logs_dir, f"{timestamp}_errors.log")

logger = logging.getLogger(app_name)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)-16s:%(lineno)-5d] %(message)s")

main_handler = RotatingFileHandler(main_log_file, maxBytes=10_000_000, backupCount=5)
main_handler.setFormatter(formatter)
main_handler.setLevel(logging.INFO)

error_handler = RotatingFileHandler(error_log_file, maxBytes=10_000_000, backupCount=5)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(main_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)
