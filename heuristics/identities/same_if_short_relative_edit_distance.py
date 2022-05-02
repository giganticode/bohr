from typing import Optional, Tuple

import Levenshtein
from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_same_names(identities: Tuple[Identity, Identity]) -> Optional[Labels]:
    """
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babiy"]})))
    MatchLabel.Match
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Andrew Babii"]})))
    MatchLabel.NoMatch
    """
    name1 = identities[0].name
    name2 = identities[1].name
    distance = Levenshtein.distance(name1, name2)
    maxLength = max(len(name1), len(name2))
    return (
        MatchLabel.Match
        if (maxLength - distance) / maxLength >= 0.8
        else MatchLabel.NoMatch
    )
