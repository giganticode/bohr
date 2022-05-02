from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_contains_large_two_part_name(
    identities: Tuple[Identity, Identity]
) -> Optional[Labels]:
    """
    >>> same_if_contains_large_two_part_name((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babii, the programmer"]})))
    MatchLabel.Match
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if len(name1) >= 10 and len(name1.split(" ")) >= 2 and name1 in name2:
        return MatchLabel.Match
