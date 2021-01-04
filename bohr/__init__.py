import logging
from pathlib import Path

from rich.logging import RichHandler

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
TEST_DIR = DATA_DIR / "test"
TRAIN_DIR = DATA_DIR / "train"
HEURISTIC_DIR = PROJECT_DIR / "bohr" / "heuristics"
DATASET_DIR = PROJECT_DIR / "bohr" / "datasets"
LABELED_DATA_DIR = PROJECT_DIR / "labeled-data"


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("bohr")
