from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def not_same_if_only_first_names_match(
    identities: Tuple[Identity, Identity]
) -> Optional[Labels]:
    """
    >>> not_same_if_only_first_names_match((Identity({"names": ["Hlib Mr Babii"]}), Identity({"names": ["Hlib Babii"]})))
    MatchLabel.Match
    >>> not_same_if_only_first_names_match((Identity({"names": ["Hlib Babii Mr"]}), Identity({"names": ["Hlib Babii"]}))) is None
    True
    """
    if len(spl1 := identities[0].name.split(" ")) != len(
        spl2 := identities[1].name.split(" ")
    ):
        if spl1[0] == spl2[0] and spl1[-1] == spl2[-1]:
            return MatchLabel.Match
