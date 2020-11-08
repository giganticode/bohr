from typing import Optional, Callable, Mapping, Any, List

from cachetools import LRUCache
from snorkel.labeling import LabelingFunction, labeling_function
from snorkel.map import BaseMapper
from snorkel.preprocess import BasePreprocessor
from snorkel.types import DataPoint

from bohr import PROJECT_DIR
from bohr.artifacts.commits import Commit
from bohr.labels import Label
from bohr.params import LABEL_CATEGORIES
from bohr.pipeline.parse_labels import FlattenedLabelHierarchy

flattened_label_hierarchy = FlattenedLabelHierarchy.load(PROJECT_DIR / 'bohr' / 'labels_dict.json')
bohr_to_snorkel_labels_map = flattened_label_hierarchy.get_category_map(LABEL_CATEGORIES)


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


def to_snorkel_label(label: Label) -> int:
    if label is None:
        return -1
    snorkel_label = bohr_to_snorkel_labels_map[type(label).__name__]
    if snorkel_label == 'Label':
        return len(LABEL_CATEGORIES)

    return LABEL_CATEGORIES.index(snorkel_label)


class commit_lf(labeling_function):
    def __call__(self, f: Callable[..., Label]) -> LabelingFunction:
        name = self.name or f.__name__
        return CommitLabelingFunction(name=name, f=lambda *args: to_snorkel_label(f(*args)), resources=self.resources, pre=self.pre)