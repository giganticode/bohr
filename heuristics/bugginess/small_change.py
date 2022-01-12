from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def small_change(commit: Commit) -> Optional[Labels]:
    if 'bohr' in commit.raw_data and 'gt_512_codeberta_tokens' in commit.raw_data['bohr']:
       if not commit.raw_data['bohr']['gt_512_codeberta_tokens']:
           return CommitLabel.BugFix
    return None
