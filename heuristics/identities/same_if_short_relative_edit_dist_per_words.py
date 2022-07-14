from typing import Optional, Tuple

import Levenshtein
from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_short_relative_edit_dist_per_words(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> same_if_short_relative_edit_dist_per_words((Identity({"names": ["Hlib Bue"]}), Identity({"names": ["Hlib Babiy"]})))
    MatchLabel.NoMatch
    >>> same_if_short_relative_edit_dist_per_words((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Andrew Babii"]})))
    MatchLabel.NoMatch
    >>> same_if_short_relative_edit_dist_per_words((Identity({"names": ["Andrii Babii"]}), Identity({"names": ["Andrew Babii"]})))
    MatchLabel.Match
    >>> same_if_short_relative_edit_dist_per_words((Identity({}), Identity({}))) is None
    True
    """
    name1 = identities[0].name
    name2 = identities[1].name
    if name1 is not None and name2 is not None:
        if len(spl1 := name1.split(" ")) >= 2 and len(spl2 := name2.split(" ")) >= 2:
            distance1 = Levenshtein.distance(spl1[0], spl2[0])
            distance2 = Levenshtein.distance(spl1[1], spl2[1])
            max_length1 = max(len(spl1[0]), len(spl2[0]))
            max_length2 = max(len(spl1[1]), len(spl2[1]))
            return (
                MatchLabel.Match
                if min(
                    (max_length1 - distance1) / max_length1,
                    (max_length2 - distance2) / max_length2,
                )
                >= 0.6
                else MatchLabel.NoMatch
            )
