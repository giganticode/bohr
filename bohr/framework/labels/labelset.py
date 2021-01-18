from dataclasses import dataclass
from enum import Flag, auto
from functools import reduce
from typing import List, Set, Type, TypeVar, Union


class Label(Flag):
    def __or__(self, other: Union["LabelSet", "Label"]):
        if type(self) == type(other):
            return super().__or__(other)
        else:
            return LabelSet.of(self) | other

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    @classmethod
    def hierarchy_root(cls: Type["Label"]) -> "Label":
        return reduce(lambda x, y: x | y, cls)

    def is_ancestor_of(self, child: "Label") -> bool:
        if child is None:
            return False
        if type(self) == type(child):
            return self | child == self and self & child == child

        if not hasattr(child, "parent"):
            raise ValueError(
                "Incorrectly defined class. All classes inherited from label must have method 'parent()'"
            )

        return self.is_ancestor_of(child.parent())


LabelSubclass = TypeVar("LabelSubclass", bound=Label)


@dataclass(frozen=True)
class LabelSet:
    """
    >>> class A(Label):
    ...    A3 = auto()
    ...    A41 = auto()
    ...    A42 = auto()
    ...    A4 = A41 | A42
    ...    A21 = auto()
    ...    A22 = auto()
    ...    A2 = A21 | A22
    ...    A0 = A2 | A3 | A4
    ...
    ...    def parent(cls):
    ...        return None

    >>> class B(Label):
    ...     B22 = auto()
    ...     B21 = auto()
    ...     A2 = B21 | B22
    ...
    ...     def parent(cls):
    ...         return A.A2

    >>> class C(Label):
    ...    C41 = auto()
    ...    C42 = auto()
    ...    A4 = C41 | C42
    ...
    ...    def parent(cls):
    ...        return A.A4

    #                             A0 <-A
    #                         /   |     \
    #     A2 <-B -------   [A2]   [A3]      [A4]  ----------  A4 <-C
    #   /  \               / \               /  \            /   \
    # B21  B22           A21  A22         A41   A42       (C41)   C42

    >>> C.C41.is_ancestor_of(A.A4)
    False
    >>> A.A2.is_ancestor_of(B.B21)
    True
    >>> A.A0.is_ancestor_of(C.C42)
    True
    >>> A.A3.is_ancestor_of(C.C42)
    False
    >>> A.A3.is_ancestor_of(A.A3)
    True
    >>> C.C41.is_ancestor_of(B.B21)
    False

    >>> import sys
    >>> sys.modules[__name__].__dict__.update({'A': A, 'B': B, 'C': C})

    >>> label_set = LabelSet.of(A.A2, B.B21)
    >>> label_set
    {A.A2, B.B21}
    >>> label_set | C.C41
    {A.A2, B.B21, C.C41}
    >>> label_set | A.A21
    {A.A2, B.B21}
    >>> label_set | A.A0
    {A.A0, B.B21}
    >>> label_set | LabelSet.of(C.C41)
    {A.A2, B.B21, C.C41}
    >>> label_set | LabelSet.of(A.A21)
    {A.A2, B.B21}

    >>> LabelSet.of(A.A2).distribute_into_categories([A.A3, A.A4, B.B21])
    Traceback (most recent call last):
    ...
    ValueError: All categories should be from the same hierarchy. However you have categories from different hierarchies: A.A3 and B.B21
    >>> LabelSet.of(C.C41).distribute_into_categories([A.A3, A.A4])
    A.A4
    >>> LabelSet.of(A.A42, C.C41).distribute_into_categories([A.A3, A.A4])
    A.A4
    >>> LabelSet.of(A.A3).distribute_into_categories([A.A3, A.A4])
    A.A3
    >>> LabelSet.of(A.A0).distribute_into_categories([A.A3, A.A4])
    A.A0
    >>> LabelSet.of(A.A2).distribute_into_categories([A.A3, A.A4])
    A.A0
    """

    labels: Set[LabelSubclass]

    def __post_init__(self):
        if not isinstance(self.labels, frozenset):
            raise ValueError(f"Labels should be a frozenset but is {type(self.labels)}")

    @classmethod
    def of(cls, *labels: LabelSubclass):
        res = set()
        for label in labels:
            res = LabelSet._add_label(res, label)
        return cls(frozenset(res))

    def __repr__(self) -> str:
        sorted_labels = sorted(self.labels, key=lambda l: l.__class__.__name__)
        return "{" + ", ".join(map(lambda l: repr(l), sorted_labels)) + "}"

    @staticmethod
    def _add_label(
        labels: Set[LabelSubclass], label_to_add: LabelSubclass
    ) -> Set[LabelSubclass]:
        flag_to_remove = None
        for flag in labels:
            if type(flag) == type(label_to_add):
                flag_to_remove = flag
                label_to_add = label_to_add | flag
                break
        if flag_to_remove:
            labels.remove(flag_to_remove)
        labels.add(label_to_add)
        return labels

    def __or__(self, other: Union["LabelSet", Label]) -> "LabelSet":
        label_set = other if isinstance(other, LabelSet) else LabelSet.of(other)

        new_label_set = set(self.labels)
        for label in label_set.labels:
            new_label_set = LabelSet._add_label(new_label_set, label)

        return LabelSet(frozenset(new_label_set))

    def distribute_into_categories(
        self, categories: List[LabelSubclass]
    ) -> LabelSubclass:
        if not categories:
            raise ValueError("List of categories cannot be empty")
        categories_union = categories[0]

        for category in categories:
            if type(category) != type(categories[0]):
                raise ValueError(
                    "All categories should be from the same hierarchy. "
                    f"However you have categories from different hierarchies: {categories[0]} and {category}"
                )
            categories_union |= category

        result = type(categories_union).hierarchy_root()
        for label in self.labels:
            if categories_union.is_ancestor_of(label):
                while type(label) != type(categories_union):
                    label = label.parent()
                for category in categories:
                    if category & label:
                        result &= category | label

        return result


Labels = Union[Label, LabelSet]
