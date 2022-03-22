from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrapi.util.extensiontypes import code_extensions, passive_code_extensions
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def buggless_if_one_file_markdown_ext(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) != 1:
        return None
    filename = str(commit.commit_files[0].filename)
    if filename.split(".")[-1] == 'md':
        return CommitLabel.NonBugFix
    else:
        return None
