from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from labels import CommitLabel


@Heuristic(Commit)
def removed_fixme(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        for change in file.parsed_changes:
            if (
                change[0] == "del" and "FIXME" in change[1]
            ):  # TODO check some papers on technical debt for the ways the mine SATD and conclusion drawn
                return (
                    CommitLabel.BugFix
                )  # TODO looks like these things are removed not by bug fixes but rather by just removing FIXMEs and TODOs :)
    return None  # TODO Should we just create labels smth like SadtRemoval
