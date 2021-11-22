from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrapi.util.extensiontypes import code_extensions, passive_code_extensions
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bugless_if_not_code_files(commit: Commit) -> Optional[Labels]:
    file_found = False
    for file in commit.commit_files:
        if isinstance(file.filename, float):
            continue  # TODO filename is NaN if it's not given <- needs to be fixed!
        if file.filename.split(".")[-1] in [*code_extensions, *passive_code_extensions]:
            # TODO move filetype logic to CommitFile artifact?
            return None
        else:
            file_found = True
    return CommitLabel.NonBugFix if file_found else None
