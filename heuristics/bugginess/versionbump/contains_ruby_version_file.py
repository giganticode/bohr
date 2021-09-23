from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def contains_ruby_version_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == ".ruby-version" and file.status == "modified":
            return CommitLabel.DependencyVersionBump
    return None
