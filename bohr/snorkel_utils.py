from functools import wraps
from typing import Optional

import snorkel
from snorkel.labeling import labeling_function

Label = int

BUG = 1
BUGLESS = 0
ABSTAIN = -1


def heuristic(name: Optional[str] = None):
    """
    This decorator is similar to @labeling_function but preserves the docstring
    """
    def wrapper(func):
        return wraps(func)(snorkel.labeling.LabelingFunction(name=name or func.__name__, f=func))
    return wrapper
