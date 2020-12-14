import logging
import sys
from typing import Type, Tuple, List

from cachetools import LRUCache

from bohr.params import LABEL_CATEGORIES
from bohr.pipeline.labels.labelset import LabelSet, LabelSubclass


logger = logging.getLogger(__name__)


def get_category_objets() -> Tuple[Type[LabelSubclass], List[LabelSubclass]]:
    category_hierarchy_name = LABEL_CATEGORIES[0].split(".")[0]
    category_hierarchy = getattr(sys.modules['bohr.labels'], category_hierarchy_name)
    for label in LABEL_CATEGORIES:
        if label.split('.')[0] != category_hierarchy_name:
            raise ValueError(f"Cannot specify categories from different hierarchies: {LABEL_CATEGORIES[0]} and {label}")
    labelsq = [category_hierarchy[label_str.split(".")[1]] for label_str in LABEL_CATEGORIES]
    return category_hierarchy, labelsq


class CategoryMappingCache(LRUCache):
    """
    >>> from bohr.labels import SStuBBugFix, CommitLabel

    >>> cache = CategoryMappingCache(1)
    >>> cache.labelsq = [CommitLabel.NonBugFix, CommitLabel.BugFix]
    >>> cache[LabelSet.of(CommitLabel.NonBugFix)]
    0
    >>> cache[LabelSet.of(CommitLabel.BugFix)]
    1
    >>> cache[LabelSet.of(CommitLabel.BogusFix)]
    0
    """
    def __init__(self, maxsize):
        super().__init__(maxsize)
        self.category_hierarchy, self.labelsq = get_category_objets()

    def __missing__(self, key: LabelSet):
        label_set = key
        value = label_set.distribute_into_categories(self.labelsq)
        if value != self.category_hierarchy.hierarchy_root():
            snorkel_label = self.labelsq.index(value)
        else:
            snorkel_label = len(self.labelsq)
        self[key] = snorkel_label
        logger.info(f'Converted {key} label into {snorkel_label}')
        return snorkel_label