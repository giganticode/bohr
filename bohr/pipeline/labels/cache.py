import logging
import sys
from typing import Type, Tuple, List

from cachetools import LRUCache

from bohr.pipeline.labels.labelset import LabelSet, LabelSubclass


logger = logging.getLogger(__name__)


def get_category_objets(
    label_categories,
) -> Tuple[Type[LabelSubclass], List[LabelSubclass]]:
    category_hierarchy_name = label_categories[0].split(".")[0]
    category_hierarchy = getattr(sys.modules["bohr.labels"], category_hierarchy_name)
    for label in label_categories:
        if label.split(".")[0] != category_hierarchy_name:
            raise ValueError(
                f"Cannot specify categories from different hierarchies: {label_categories[0]} and {label}"
            )
    labelsq = [
        category_hierarchy[label_str.split(".")[1]] for label_str in label_categories
    ]
    return category_hierarchy, labelsq


class CategoryMappingCache(LRUCache):
    """
    >>> from bohr.labels import SStuBBugFix, CommitLabel
    >>> logger.setLevel("CRITICAL")

    >>> cache = CategoryMappingCache(["CommitLabel.NonBugFix", "CommitLabel.BugFix"], 10)
    >>> cache[LabelSet.of(CommitLabel.NonBugFix)]
    0
    >>> cache[LabelSet.of(CommitLabel.BugFix)]
    1
    >>> cache[LabelSet.of(CommitLabel.BogusFix)]
    0
    """

    def __init__(self, label_categories: List[str], maxsize: int):
        super().__init__(maxsize)
        self.category_hierarchy, self.labelsq = get_category_objets(label_categories)

    def __missing__(self, key: LabelSet):
        label_set = key
        value = label_set.distribute_into_categories(self.labelsq)
        if value != self.category_hierarchy.hierarchy_root():
            snorkel_label = self.labelsq.index(value)
        else:
            snorkel_label = len(self.labelsq)
        self[key] = snorkel_label
        logger.info(f"Converted {key} label into {snorkel_label}")
        return snorkel_label
