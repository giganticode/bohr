from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def not_same_if_only_first_names_match(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> not_same_if_only_first_names_match((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Shevchuk"]})))
    MatchLabel.NoMatch
    >>> not_same_if_only_first_names_match((Identity({}), Identity({}))) is None
    True
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if name1 is not None and name2 is not None:
        if len(spl1 := name1.split(" ")) == 2 and len(spl2 := name2.split(" ")) == 2:
            if spl1[0] == spl2[0] and spl1[1] != spl2[1]:
                return MatchLabel.NoMatch
