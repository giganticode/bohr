from typing import Optional, Tuple

import Levenshtein
from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_short_relative_edit_distance(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babiy"]})))
    MatchLabel.Match
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Andrew Babii"]})))
    MatchLabel.NoMatch
    >>> same_if_same_names((Identity({}), Identity({}))) is None
    True
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if name1 is not None and name2 is not None:
        distance = Levenshtein.distance(name1, name2)
        max_length = max(len(name1), len(name2))
        return (
            MatchLabel.Match
            if (max_length - distance) / max_length >= 0.8
            else MatchLabel.NoMatch
        )
