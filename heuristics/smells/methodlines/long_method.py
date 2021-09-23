from typing import Optional

from bohrapi.artifacts import Method
from bohrapi.core import Heuristic
from bohrlabels.core import Label
from bohrlabels.labels import SnippetLabel


@Heuristic(Method)
def long_method(method: Method) -> Optional[Label]:
    if len(method.lines) > 30:
        return SnippetLabel.LongMethod
    else:
        return None
