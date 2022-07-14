from typing import Optional

from bohrapi.artifacts import Method
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import SnippetLabel


@Heuristic(Method)
def many_indentation_levels2(method: Method) -> Optional[OneOrManyLabels]:
    if method.max_depth > 6:
        return SnippetLabel.LongMethod
    else:
        return None
