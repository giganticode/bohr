import logging
import sys

from bohr.artifacts.commit import Commit
from bohr.pathconfig import PathConfig
from bohr.templates.heuristics.tool import Tool

logger = logging.getLogger(__name__)


class IdansCorrectiveModel(Tool):
    def __init__(self, path_config: PathConfig):
        super().__init__(path_config)
        sys.path.append(str(path_config.software_path / "commit-classification"))
        logger.debug(
            f"Adding Idan's commit classification tool to path.\n PYTHONPATH is {sys.path}"
        )

    def check_installed(self):
        pass

    def run(self, commit: Commit) -> bool:
        from corrective_model import is_fix

        return is_fix(commit.message.raw)
