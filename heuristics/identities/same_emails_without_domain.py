from typing import Optional, Tuple

from bohrapi.artifacts.identity import Identity
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import MatchLabel


@Heuristic(Identity, Identity)
def same_emails_without_domain(
    identities: Tuple[Identity, Identity]
) -> Optional[OneOrManyLabels]:
    """
    >>> same_emails_without_domain((Identity({"emails": ["hbabii@gmail.com"]}), Identity({"emails": ["hbabii@unibz.it"]})))
    MatchLabel.Match
    >>> same_emails_without_domain((Identity({"emails": ["a@a.com"]}), Identity({"emails": ["b@b.com"]}))) is None
    True
    """
    name1 = identities[0].normalized_email
    name2 = identities[1].normalized_email
    if name1 == name2:
        return MatchLabel.Match
