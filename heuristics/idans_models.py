from typing import Optional

from bohr.artifacts.commit import Commit
from bohr.labels.labelset import Labels
from bohr.templates.heuristics.tool import ToolOutputHeuristic
from heuristics.tools.idansmodel import IdansCorrectiveModel
from labels import CommitLabel


@ToolOutputHeuristic(Commit, tool=IdansCorrectiveModel)
def is_fix(
    commit: Commit, idans_corrective_model: IdansCorrectiveModel
) -> Optional[Labels]:
    result = idans_corrective_model.run(commit)
    if result:
        return CommitLabel.BugFix
    else:
        return CommitLabel.NonBugFix
