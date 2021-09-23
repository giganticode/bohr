from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrapi.util.extensiontypes import code_extensions, passive_code_extensions
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bug_if_only_changed_lines_in_one_code_file(commit: Commit) -> Optional[Labels]:
    if (
            len(commit.commit_files) == 1
            and commit.commit_files[0].status == "modified"
            and not isinstance(commit.commit_files[0].filename, float)
            and commit.commit_files[0].filename.split(".")[-1]
            in [*code_extensions, *passive_code_extensions]
            and commit.commit_files[0].changes
            and commit.commit_files[0].no_added_lines()
            and commit.commit_files[0].no_removed_lines()
    ):
        return CommitLabel.BugFix
    return None
