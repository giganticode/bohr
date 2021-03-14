from pathlib import Path
from typing import Optional, Type

from cachetools import LRUCache
from snorkel.types import DataPoint

from bohr.artifacts.commit import Commit
from bohr.core import ArtifactMapper


class IdansCommitMapper(ArtifactMapper):

    cache = LRUCache(512)

    def __init__(self, project_root: Optional[Path]) -> None:
        super().__init__("CommitMapper", [], memoize=False)
        self.project_root = project_root

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.repo_name, x.commit)
        if key in self.cache:
            return self.cache[key]

        commit = Commit(None, x.repo_name, x.commit, str(x.message), self.project_root)
        self.cache[key] = commit

        return commit

    def get_artifact(self) -> Type:
        return Commit
