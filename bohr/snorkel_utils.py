from typing import Optional, Callable, Mapping, Any, List

from cachetools import LRUCache
from snorkel.labeling import LabelingFunction, labeling_function
from snorkel.map import BaseMapper
from snorkel.preprocess import BasePreprocessor
from snorkel.types import DataPoint

from bohr.artifacts.commits import Commit
from bohr.labels import Label


class CommitMapper(BaseMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__('CommitMapper', [], memoize=False)

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.owner, x.repository, x.sha)
        if key in self.cache:
            return self.cache[key]

        commit = Commit(x.owner, x.repository, x.sha, x.message)
        self.cache[key] = commit

        return commit


class CommitLabelingFunction(LabelingFunction):
    def __init__(
        self,
        name: str,
        f: Callable[..., int],
        resources: Optional[Mapping[str, Any]] = None,
        pre: Optional[List[BasePreprocessor]] = None,
    ) -> None:
        if pre is None:
            pre = []
        pre.insert(0, CommitMapper())
        super().__init__(name, f, resources, pre=pre)


class commit_lf(labeling_function):
    def __call__(self, f: Callable[..., Label]) -> LabelingFunction:
        name = self.name or f.__name__
        return CommitLabelingFunction(name=name, f=lambda *args: f(*args).value, resources=self.resources, pre=self.pre)