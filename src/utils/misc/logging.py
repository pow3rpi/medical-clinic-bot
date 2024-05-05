import logging.handlers

from src.core import secrets

logger = logging.getLogger(__name__)

file_handler = logging.handlers.RotatingFileHandler(
    filename=secrets.LOG_PATH + 'admin_logs.log',
    maxBytes=secrets.LOG_SIZE,
    backupCount=secrets.N_LOGS,
    encoding=secrets.ENCODING
)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
