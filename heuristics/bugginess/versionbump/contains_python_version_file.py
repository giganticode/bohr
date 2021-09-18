from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels


@Heuristic(Commit)
def contains_python_version_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == ".python-version" and file.status == "modified":
            return l.CommitLabel.DependencyVersionBump
    return None
