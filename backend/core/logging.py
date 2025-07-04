# core/logging.py
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, serialize=True)  # JSON format
