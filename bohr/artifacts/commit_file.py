from dataclasses import dataclass
from typing import Optional

from bohr.artifacts.core import Artifact


@dataclass
class CommitFile(Artifact):
    filename: str
    status: str
    patch: Optional[str]
    changes: Optional[str]

    def no_added_lines(self):
        return "<ins>" not in self.changes

    def no_removed_lines(self):
        return "<del>" not in self.changes
