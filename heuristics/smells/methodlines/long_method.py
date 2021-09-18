from typing import Optional

from bohrapi.collection.artifacts import Method
from bohrapi.core import Heuristic
from bohrapi.labeling import Label
from labels import SnippetLabel


@Heuristic(Method)
def long_method(method: Method) -> Optional[Label]:
    if len(method.lines) > 30:
        return SnippetLabel.LongMethod
    else:
        return None
