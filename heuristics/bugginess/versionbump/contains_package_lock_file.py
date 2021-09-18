from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels


@Heuristic(Commit)
def contains_package_lock_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == "package-lock.json" and file.status == "modified":
            return l.CommitLabel.DependencyVersionBump
    return None
