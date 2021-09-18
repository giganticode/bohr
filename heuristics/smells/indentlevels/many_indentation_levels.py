from typing import Optional

from bohrapi.collection.artifacts import Method
from bohrapi.core import Heuristic
from bohrapi.labeling import Label
from labels import SnippetLabel


@Heuristic(Method)
def many_indentation_levels(method: Method) -> Optional[Label]:
    if method.max_depth > 5:
        return SnippetLabel.LongMethod
    else:
        return None
