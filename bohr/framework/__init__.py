import logging
import os
from pathlib import Path

from rich.logging import RichHandler

SOFTWARE_DIR = os.environ["SOFTWARE_DIR"]

PYTHON_ROOT = Path(__file__).parent.parent
PROJECT_DIR = PYTHON_ROOT.parent
DATA_DIR = PROJECT_DIR / "data"
LABELED_DATA_DIR = PROJECT_DIR / "labeled-data"
HEURISTIC_DIR = PYTHON_ROOT / "heuristics"
DATASET_DIR = PYTHON_ROOT / "dataloaders"
TASK_DIR = PYTHON_ROOT / "tasks"


ARTIFACT_PACKAGE = "bohr.framework.artifacts"
HEURISTIC_PACKAGE = "bohr.heuristics"
DATASET_PACKAGE = "bohr.dataloaders"
TASK_PACKAGE = "bohr.tasks"


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("bohr")
