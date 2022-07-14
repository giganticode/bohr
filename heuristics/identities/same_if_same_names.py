from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_same_names(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babii"]})))
    MatchLabel.Match
    >>> same_if_same_names((Identity({}), Identity({}))) is None
    True
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if name1 is not None and name2 is not None and name1 == name2:
        return MatchLabel.Match
