from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def contains_package_lock_file(commit: Commit) -> Optional[OneOrManyLabels]:
    for file in commit.commit_files:
        if file.filename == "package-lock.json" and file.status == "modified":
            return CommitLabel.DependencyVersionBump
    return None
