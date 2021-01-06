from typing import Optional, Type

from cachetools import LRUCache
from snorkel.types import DataPoint

from bohr.artifacts.commit import Commit
from bohr.core import ArtifactMapper


class CommitMapper(ArtifactMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__("CommitMapper", [], memoize=False)

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.owner, x.repository, x.sha)
        if key in self.cache:
            return self.cache[key]

        commit = Commit(x.owner, x.repository, x.sha, str(x.message))
        self.cache[key] = commit

        return commit

    def get_artifact(self) -> Type:
        return Commit
