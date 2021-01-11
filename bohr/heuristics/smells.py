from typing import Optional

from bohr.framework.artifacts.method import Method
from bohr.framework.core import Heuristic
from bohr.framework.labels.labelset import Label
from bohr.labels import SnippetLabel


@Heuristic(Method)
def long_method(method: Method) -> Optional[Label]:
    if len(method.lines) > 30:
        return SnippetLabel.LongMethod
    else:
        return None


@Heuristic(Method)
def many_indentation_levels(method: Method) -> Optional[Label]:
    if method.max_depth > 5:
        return SnippetLabel.LongMethod
    else:
        return None


@Heuristic(Method)
def many_indentation_levels2(method: Method) -> Optional[Label]:
    if method.max_depth > 6:
        return SnippetLabel.LongMethod
    else:
        return None
