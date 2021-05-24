from typing import Optional

import labels as l
from bohr.collection.artifacts import Method
from bohr.core import Heuristic
from bohr.labeling.labelset import Label


@Heuristic(Method)
def long_method(method: Method) -> Optional[Label]:
    if len(method.lines) > 30:
        return l.SnippetLabel.LongMethod
    else:
        return None


@Heuristic(Method)
def many_indentation_levels(method: Method) -> Optional[Label]:
    if method.max_depth > 5:
        return l.SnippetLabel.LongMethod
    else:
        return None


@Heuristic(Method)
def many_indentation_levels2(method: Method) -> Optional[Label]:
    if method.max_depth > 6:
        return l.SnippetLabel.LongMethod
    else:
        return None
