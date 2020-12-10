import json
import logging
from pathlib import Path
from typing import List, Tuple

from bohr import PROJECT_DIR
from bohr.pipeline.labels.hierarchies import LabelHierarchy

logger = logging.getLogger(__name__)

PATH_TO_LABELS_DIR = PROJECT_DIR / 'bohr' / 'labels'


def load(f: List[str]) -> List[Tuple[str, List[str]]]:
    res: List[Tuple[str, List[str]]] = []
    for line in f:
        spl_line: List[str] = line.strip('\n').split(":")
        if len(spl_line) != 2:
            raise ValueError(f"Invalid line: {line}\n The format must be: Parent: child1, child2, ..., childN")
        parent, children = spl_line
        res.append((parent.strip(), list(map(lambda x: x.strip(), children.split(",")))))
    return res


def build_label_tree(path_to_labels: Path) -> LabelHierarchy:
    label_file = f'{path_to_labels}/labels.txt'
    with open(label_file, 'r') as f:
        lsts = load(f.readlines())
    tree = LabelHierarchy.create_root("Label")
    for parent, children in lsts:
        node = tree.find_node_by_label(parent)
        if node.children:
            node.mounted_hierarchy = LabelHierarchy(parent, None, [])
            node = node.mounted_hierarchy
        node.add_children(children)
    return tree


def parse_label() -> None:
    label_tree = build_label_tree(PATH_TO_LABELS_DIR)
    from jinja2 import Environment, PackageLoader
    env = Environment(
        loader=PackageLoader('bohr', 'resources')
    )
    template = env.get_template('labels.template')
    s = template.render(hierarchies=label_tree.flatten())
    with open(PROJECT_DIR / 'bohr' / 'labels.py', 'w') as f:
        f.write(s)


if __name__ == '__main__':
    parse_label()

