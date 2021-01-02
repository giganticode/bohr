import logging
from glob import glob
from pathlib import Path
from typing import List, Dict, Any

from bohr import PROJECT_DIR
from bohr.pipeline.labels.hierarchies import LabelHierarchy

logger = logging.getLogger(__name__)

PATH_TO_LABELS_DIR = PROJECT_DIR / "bohr" / "labels"

FlattenedMultiHierarchy = Dict[str, List[List[str]]]


def load(f: List[str]) -> FlattenedMultiHierarchy:
    res: FlattenedMultiHierarchy = {}
    for line in f:
        spl_line: List[str] = line.strip("\n").split(":")
        if len(spl_line) != 2:
            raise ValueError(
                f"Invalid line: {line}\n The format must be: Parent: child1, child2, ..., childN"
            )
        parent, children = spl_line
        parent = parent.strip()
        if parent not in res:
            res[parent] = []
        res[parent].append(list(map(lambda x: x.strip(), children.split(","))))
    return res


def merge_dicts_(
    a: Dict[str, List[Any]], b: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    >>> a = {}
    >>> merge_dicts_(a, {})
    {}
    >>> merge_dicts_(a, {'x': ['x1']})
    {'x': ['x1']}
    >>> merge_dicts_(a, {'x': ['x2']})
    {'x': ['x1', 'x2']}
    >>> merge_dicts_(a, {'x': ['x3'], 'y': ['y1']})
    {'x': ['x1', 'x2', 'x3'], 'y': ['y1']}
    """
    for k, v in b.items():
        if k not in a:
            a[k] = []
        a[k].extend(v)
    return a


def build_label_tree(path_to_labels: Path) -> LabelHierarchy:
    flattened_multi_hierarchy: FlattenedMultiHierarchy = {}
    for label_file in sorted(glob(f"{path_to_labels}/*.txt")):
        with open(label_file, "r") as f:
            merge_dicts_(flattened_multi_hierarchy, load(f.readlines()))
    tree = LabelHierarchy.create_root("Label")
    pool = [tree]
    while len(pool) > 0:
        node = pool.pop()
        if node.label in flattened_multi_hierarchy:
            children = flattened_multi_hierarchy[node.label]
            children_nodes = node.add_children(children[0])
            pool.extend(children_nodes)
            for other_children in children[1:]:
                node.mounted_hierarchy = LabelHierarchy(node.label, None, [])
                node = node.mounted_hierarchy
                children_nodes = node.add_children(other_children)
                pool.extend(children_nodes)
    return tree


def parse_label() -> None:
    label_tree = build_label_tree(PATH_TO_LABELS_DIR)
    from jinja2 import Environment, PackageLoader

    env = Environment(loader=PackageLoader("bohr", "resources"))
    template = env.get_template("labels.template")
    s = template.render(hierarchies=label_tree.flatten())
    with open(PROJECT_DIR / "bohr" / "labels.py", "w") as f:
        f.write(s)


if __name__ == "__main__":
    parse_label()
