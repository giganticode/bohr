import logging
import functools
import sys
from typing import Optional, Callable, Mapping, Any, List

from cachetools import LRUCache
from snorkel.labeling import LabelingFunction, labeling_function
from snorkel.map import BaseMapper
from snorkel.preprocess import BasePreprocessor
from snorkel.types import DataPoint

from bohr.artifacts.commits import Commit
from bohr.pipeline.labels.cache import CategoryMappingCache

from bohr.pipeline.labels.labelset import LabelSet, Label

logger = logging.getLogger(__name__)


category_mapping_cache = CategoryMappingCache(maxsize=10000)


class CommitMapper(BaseMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__("CommitMapper", [], memoize=False)

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
        applied_to_commit: Callable[[Commit], Label],
        resources: Optional[Mapping[str, Any]] = None,
        pre: Optional[List[BasePreprocessor]] = None,
    ) -> None:
        if pre is None:
            pre = []
        pre.insert(0, CommitMapper())
        self.applied_to_commit = applied_to_commit
        super().__init__(name, f, resources, pre=pre)


def to_snorkel_label(labels) -> int:
    if labels is None:
        return -1
    label_set = labels if isinstance(labels, LabelSet) else LabelSet.of(labels)
    snorkel_label = category_mapping_cache[label_set]
    return snorkel_label


class commit_lf(labeling_function):
    def __call__(self, f: Callable[..., Label]) -> LabelingFunction:
        name = self.name or f.__name__
        func = CommitLabelingFunction(
            name=name,
            f=lambda *args: to_snorkel_label(f(*args)),
            applied_to_commit=f,
            resources=self.resources,
            pre=self.pre,
        )
        func = functools.wraps(f)(func)
        return func
