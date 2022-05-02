from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_same_names(identities: Tuple[Identity, Identity]) -> Optional[Labels]:
    """
    >>> same_if_same_names((Identity({"names": ["Hlib Babii"]}), Identity({"names": ["Hlib Babii"]})))
    MatchLabel.Match
    """
    if identities[0].name == identities[1].name:
        return MatchLabel.Match
