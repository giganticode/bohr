import logging
from typing import Any, Callable, List, Mapping, Optional

from snorkel.labeling import LabelingFunction
from snorkel.map import BaseMapper
from snorkel.preprocess import BasePreprocessor

from bohr.framework.labels.cache import CategoryMappingCache
from bohr.framework.labels.labelset import LabelSet

logger = logging.getLogger(__name__)


class SnorkelLabelingFunction(LabelingFunction):
    def __init__(
        self,
        name: str,
        f: Callable[..., int],
        mapper: BaseMapper,
        resources: Optional[Mapping[str, Any]] = None,
        pre: Optional[List[BasePreprocessor]] = None,
    ) -> None:
        if pre is None:
            pre = []
        pre.insert(0, mapper)
        super().__init__(name, f, resources, pre=pre)


def to_snorkel_label(labels, category_mapping_cache_map: CategoryMappingCache) -> int:
    if labels is None:
        return -1
    label_set = labels if isinstance(labels, LabelSet) else LabelSet.of(labels)
    snorkel_label = category_mapping_cache_map[label_set]
    return snorkel_label
