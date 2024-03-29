from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def maven_plugin_version_bump(commit: Commit) -> Optional[OneOrManyLabels]:
    if "[maven-release-plugin]" in commit.message.raw:
        return CommitLabel.VersionBump
    return None
