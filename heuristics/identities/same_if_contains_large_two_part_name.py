from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_contains_large_two_part_name(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> same_if_contains_large_two_part_name((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babii, the programmer"]})))
    MatchLabel.Match
    >>> same_if_contains_large_two_part_name((Identity({}), Identity({}))) is None
    True
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if name1 is not None and name2 is not None:
        if len(name1) >= 10 and len(name1.split(" ")) >= 2 and name1 in name2:
            return MatchLabel.Match
