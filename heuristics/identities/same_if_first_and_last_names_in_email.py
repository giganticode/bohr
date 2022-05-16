from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_if_first_and_last_names_in_email(
    identities: Tuple[Identity, Identity]
) -> Optional[Labels]:
    """
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["hlibbabii@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"names": ["hlib babii"]}), Identity({"emails": ["hlibbabii@gmail.com"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["hbabii@gmail.com"]}), Identity({"names": ["hlib babii"]}))) is None
    True
    >>> same_if_first_and_last_names_in_email((Identity({}), Identity({}))) is None
    True
    """
    if (email := identities[0].email) is not None and (
        name := identities[1].name
    ) is not None:
        pass
    elif (email := identities[1].email) is not None and (
        name := identities[0].name
    ) is not None:
        pass
    else:
        return

    if len(spl := name.split(" ")) >= 2:
        if len(first_name := spl[0]) > 1 and len(last_name := spl[-1]) > 1:
            if first_name in email and last_name in email:
                return MatchLabel.Match
