from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class ParentHierarchy:
    name: str
    mount_point: str


FlattenedNodes = List[Tuple[str, List[str]]]


@dataclass
class FlattenedHierarchy:
    name: str
    parent_hierarchy: Optional[ParentHierarchy]
    nodes: FlattenedNodes = field(default_factory=list)


@dataclass
class LabelHierarchy:
    """
    >>> root_label = LabelHierarchy.create_root("Label")
    >>> commit, = root_label.add_children(["Commit"])
    >>> bug_fix, refactoring, feature = commit.add_children(["BugFix", "Refactoring", "Feature"])
    >>> minor_refactoring, major_refactoring = refactoring.add_children(["MinorRefactoring", "MajorRefactoring"])
    >>> refactoring.mounted_hierarchy = LabelHierarchy.create_root("Refactoring")
    >>> moving, renaming = refactoring.mounted_hierarchy.add_children(["Moving", "Renaming"])
    >>> minor, major, critical, other = bug_fix.add_children(["Minor", "Major", "Critical", "OtherSeverityLevel"])
    >>> commit.mounted_hierarchy = LabelHierarchy.create_root("Commit")
    >>> tangled, non_tangled = commit.mounted_hierarchy.add_children(["Tangled", "NonTangled"])

    >>> from pprint import pprint
    >>> pprint(root_label.flatten())
    [FlattenedHierarchy(name='CommitLabel', parent_hierarchy=None, nodes=[('Minor', []), ('Major', []), ('Critical', []), ('OtherSeverityLevel', []), ('BugFix', ['Minor', 'Major', 'Critical', 'OtherSeverityLevel']), ('MinorRefactoring', []), ('MajorRefactoring', []), ('Refactoring', ['MinorRefactoring', 'MajorRefactoring']), ('Feature', []), ('Commit', ['BugFix', 'Refactoring', 'Feature']), ('Label', ['Commit'])]),
     FlattenedHierarchy(name='MovingRefactoring', parent_hierarchy=ParentHierarchy(name='CommitLabel', mount_point='Refactoring'), nodes=[('Moving', []), ('Renaming', []), ('Refactoring', ['Moving', 'Renaming'])]),
     FlattenedHierarchy(name='TangledCommit', parent_hierarchy=ParentHierarchy(name='CommitLabel', mount_point='Commit'), nodes=[('Tangled', []), ('NonTangled', []), ('Commit', ['Tangled', 'NonTangled'])])]
    """

    label: str
    parent: Optional["LabelHierarchy"]
    children: List["LabelHierarchy"]
    mounted_hierarchy: Optional["LabelHierarchy"] = None

    def __repr__(self) -> str:
        res = self.label
        if self.children:
            res += (
                "{"
                + "|".join(map(lambda x: str(x), self.children))
                + "}"
                + f"-> {self.mounted_hierarchy}"
            )
        return res

    @classmethod
    def create_root(cls, label: str) -> "LabelHierarchy":
        return cls(label, None, [])

    def add_children(self, children: List[str]) -> List["LabelHierarchy"]:
        self.children = [LabelHierarchy(child, self, []) for child in children]
        return self.children

    def flatten(
        self, parent: Optional[ParentHierarchy] = None
    ) -> List[FlattenedHierarchy]:
        hirarchy_name = f"{self.children[0].label}{self.label}"
        hierarchy_tail, other_hierarchies = self._flatten(hirarchy_name)
        return [
            FlattenedHierarchy(hirarchy_name, parent, hierarchy_tail)
        ] + other_hierarchies

    def _flatten(
        self, hierarchy_top: Optional["str"] = None
    ) -> Tuple[FlattenedNodes, List[FlattenedHierarchy]]:
        other_hierarchies: List[FlattenedHierarchy] = []
        main_hierarchy_nodes: FlattenedNodes = []
        for child in self.children:
            child_nodes, lst = child._flatten(hierarchy_top)
            other_hierarchies.extend(lst)
            main_hierarchy_nodes.extend(child_nodes)
        main_hierarchy_nodes.append(
            (self.label, list(map(lambda c: c.label, self.children)))
        )
        if self.mounted_hierarchy:
            other_hierarchies += self.mounted_hierarchy.flatten(
                ParentHierarchy(hierarchy_top, self.label)
            )
        return main_hierarchy_nodes, other_hierarchies
