import re
from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels


@Heuristic(Commit)
def maven_plugin_version_bump(commit: Commit) -> Optional[Labels]:
    if "[maven-release-plugin]" in commit.message.raw:
        return l.CommitLabel.VersionBump
    return None
