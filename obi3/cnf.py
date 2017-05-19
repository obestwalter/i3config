import logging
import sys
from pathlib import Path


PROJECT_PATH = Path(__file__).parents[1]
fragmentsPath = PROJECT_PATH / 'mine'
CONFIG_PATH = PROJECT_PATH / 'config'
suffix = '.i3conf'


def configure_logging():
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout, format=fmt, level=logging.INFO)
