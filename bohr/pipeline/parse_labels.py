import glob
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pprint
from typing import List, Optional, Dict, Union

from yaml import YAMLError, safe_load

from bohr import PROJECT_DIR

logger = logging.getLogger(__name__)

PATH_TO_LABELS_DIR = PROJECT_DIR / 'bohr' / 'labels'


@dataclass
class LabelClass:
    name: str
    parent: str


LabelHierarchy = Dict[str, Union[str, 'LabelHierarchy']]


@dataclass
class FlattenedLabelHierarchy:
    labels: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> 'FlattenedLabelHierarchy':
        with open(path, 'r') as f:
            return cls(json.load(f))

    def dump(self, path: Path) -> None:
        with open(path, 'w') as f:
            json.dump(self.labels, f)

    def get_parent(self, x: str) -> Optional[str]:
        try:
            return self.labels[x]
        except KeyError:
            return None

    def is_ancestor(self, x: str, y: str):
        """
        >>> h = FlattenedLabelHierarchy({'b': 'a', 'c': 'b'})
        >>> h.is_ancestor('a', 'a')
        True
        >>> h.is_ancestor('b', 'a')
        True
        >>> h.is_ancestor('c', 'a')
        True
        >>> h.is_ancestor('a', 'b')
        False
        """
        if x is None:
            return False
        elif x == y:
            return True

        return self.is_ancestor(self.get_parent(x), y)

    def most_general_label_in_category(self, x: str, lst: List[str]) -> str:
        """
        >>> h = FlattenedLabelHierarchy({"BugFix": "Label", "NonBugFix": "Label", "BogusFix": "NonBugFix", \
"DocFix": "BogusFix", "TestFix": "BogusFix"})
        >>> h.most_general_label_in_category("TestFix", ["BugFix", "NonBugFix"])
        'NonBugFix'
        >>> h.most_general_label_in_category("BugFix", ["BugFix", "NonBugFix"])
        'BugFix'
        >>> h.most_general_label_in_category("DocFix", ["TestFix"])
        'Label'
        >>> h.most_general_label_in_category("DocFix", ["Label"])
        Traceback (most recent call last):
        ...
        ValueError: Bad label: Label
        >>> h.most_general_label_in_category("DocFix", ["UnknownLabel"])
        Traceback (most recent call last):
        ...
        ValueError: Bad label: UnknownLabel
        """
        if x not in self.labels and x != 'Label':
            raise ValueError(f"Bad label: {x}")

        for l in lst:
            if l not in self.labels:
                raise ValueError(f"Bad label: {l}")

        if x in lst:
            return x

        parent = self.get_parent(x)
        if parent is None:
            return x
        return self.most_general_label_in_category(parent, lst)

    def get_category_map(self, lst: List[str]) -> Dict[str, str]:
        res: Dict[str, str] = {}
        for label in self.labels:
            res[label] = self.most_general_label_in_category(label, lst)
        return res

    def safe_add(self, new_label_class: LabelClass) -> 'FlattenedLabelHierarchy':
        """
        >>> h = FlattenedLabelHierarchy({'b': 'a', 'c': 'b'})
        >>> h.safe_add(LabelClass('g', 'h'))
        Traceback (most recent call last):
        ...
        ValueError: Unknown parent: h
        >>> h.safe_add(LabelClass('d', 'c'))
        FlattenedLabelHierarchy(labels={'b': 'a', 'c': 'b', 'd': 'c'})
        >>> h.safe_add(LabelClass('b', 'a'))
        FlattenedLabelHierarchy(labels={'b': 'a', 'c': 'b', 'd': 'c'})
        >>> h.safe_add(LabelClass('d', 'a'))
        FlattenedLabelHierarchy(labels={'b': 'a', 'c': 'b', 'd': 'c'})
        >>> h.safe_add(LabelClass('e', 'b'))
        FlattenedLabelHierarchy(labels={'b': 'a', 'c': 'b', 'd': 'c', 'e': 'b'})
        """
        if new_label_class.name in self.labels:
            parent_to_add = new_label_class.parent
            existing_parent = self.get_parent(new_label_class.name)
            if not self.is_ancestor(parent_to_add, existing_parent) and not self.is_ancestor(existing_parent, parent_to_add):
                raise ValueError(f"Duplicated label {new_label_class.name} with different parents: {parent_to_add} and {existing_parent}")
        elif new_label_class.parent not in self.labels and new_label_class.parent != 'Label':
            raise ValueError(f'Unknown parent: {new_label_class.parent}')
        else:
            self.labels[new_label_class.name] = new_label_class.parent

        return self

    def __iter__(self):
        return iter([LabelClass(k, v) for k, v in self.labels.items()])


def flatten_label_lists(label_hierarchy_list: List[LabelHierarchy]) -> FlattenedLabelHierarchy:
    all = FlattenedLabelHierarchy()
    for label_hierarchy in label_hierarchy_list:
        all = flatten_label_list(all, label_hierarchy)
    return all


def flatten_label_list(res: FlattenedLabelHierarchy, label_hierarchy: LabelHierarchy, root: Optional[str] = None) -> FlattenedLabelHierarchy:
    parent = next(iter(label_hierarchy))
    if root:
        res.safe_add(LabelClass(parent, root))
    classes = label_hierarchy[parent]
    for clazz in classes:
        if isinstance(clazz, str):
            res.safe_add(LabelClass(clazz, parent))
        else:
            for l in flatten_label_list(res, clazz, parent):
                res.safe_add(l)
    return res


def load_labels(path_to_labels: Path) -> List[LabelHierarchy]:
    label_lists = []
    for label_file in glob.glob(f'{path_to_labels}/*.yaml'):
        with open(label_file, 'r') as f:
            try:
                label_lists.append({"Label": safe_load(f)})
            except YAMLError as exc:
                logger.error(f'Failed to load file with labels: {label_file}', exc)
    return label_lists


def parse_label() -> None:
    label_lists = load_labels(PATH_TO_LABELS_DIR)
    flattened_label_hierarchy: FlattenedLabelHierarchy = flatten_label_lists(label_lists)
    flattened_label_hierarchy.dump(PROJECT_DIR / 'bohr' / 'labels_dict.json')
    flattened_label_list = [l for l in flattened_label_hierarchy]
    pprint(flattened_label_list)
    from jinja2 import Environment, PackageLoader
    env = Environment(
        loader=PackageLoader('bohr', 'resources')
    )
    template = env.get_template('labels.template')
    s = template.render(classes=flattened_label_list)
    with open(PROJECT_DIR / 'bohr' / 'labels.py', 'w') as f:
        f.write(s)


if __name__ == '__main__':
    parse_label()

