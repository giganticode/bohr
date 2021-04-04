from typing import Optional

import labels as l
from bohr.artifacts.method import Method
from bohr.decorators import Heuristic
from bohr.labels.labelset import Label


@Heuristic(Method)
def long_method_test(method: Method) -> Optional[Label]:
    if len(method.lines) > 10:
        return l.SnippetLabel.LongMethod
    else:
        return None
