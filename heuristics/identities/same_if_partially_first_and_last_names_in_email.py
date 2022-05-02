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
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["hbabii@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["babiih@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["hlibb@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["bhlib@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    >>> same_if_first_and_last_names_in_email((Identity({"emails": ["hlibbabii@gmail.com"]}), Identity({"names": ["hlib babii"]})))
    MatchLabel.Match
    """
    email = identities[0].email
    name = identities[1].name
    if email is not None and name is not None:
        if len(spl := name.split(" ")) >= 2:
            if len(first_name := spl[0]) > 2 and len(last_name := spl[-1]) > 2:
                if (first_name[:1] + last_name) in email:
                    return MatchLabel.Match
                if (first_name + last_name[:1]) in email:
                    return MatchLabel.Match
                if (last_name[:1] + first_name) in email:
                    return MatchLabel.Match
                if (last_name + first_name[:1]) in email:
                    return MatchLabel.Match
