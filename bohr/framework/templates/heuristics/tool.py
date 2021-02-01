import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Type

import regex

from bohr.framework.artifacts.commit import Commit
from bohr.framework.artifacts.core import Artifact
from bohr.framework.core import Heuristic, _Heuristic
from bohr.framework.labels.labelset import Labels

logger = logging.getLogger(__name__)


# TODO move to some proper place
def camel_case_to_snake_case(identifier: str) -> str:
    parts = [
        m[0]
        for m in regex.finditer(
            "(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]])|[^ ])",
            identifier,
        )
    ]
    return "_".join(parts).lower()


class Tool(ABC):
    @abstractmethod
    def check_installed(self):
        pass

    @abstractmethod
    def run(self, artifact: Artifact) -> Any:
        pass


class ToolOutputHeuristic(Heuristic):
    def __init__(
        self,
        artifact_type_applied_to: Type[Artifact],
        tool: Type[Tool],
        resources=None,
    ):
        super().__init__(artifact_type_applied_to)
        self.resources = resources
        self.tool = tool()
        self.tool.check_installed()

    def __call__(self, f: Callable[[Commit, Tool], Optional[Labels]]) -> _Heuristic:

        safe_func = self.get_artifact_safe_func(f)

        heuristic = _Heuristic(
            safe_func,
            artifact_type_applied_to=self.artifact_type_applied_to,
            resources={camel_case_to_snake_case(type(self.tool).__name__): self.tool},
        )

        return heuristic
