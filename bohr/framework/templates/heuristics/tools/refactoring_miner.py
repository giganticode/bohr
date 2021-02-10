import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

import jsons

from bohr.framework.artifacts.commit import Commit
from bohr.framework.templates.heuristics.tool import Tool
from bohr.framework.templates.heuristics.tools import SOFTWARE_DIR

REFACTORING_MINER_PATH = Path(SOFTWARE_DIR) / "RefactoringMiner-2.0.3" / "bin"


@dataclass
class RefactoringMinerCommit:
    repository: str
    sha1: str
    url: str
    refactorings: List


@dataclass
class RefactoringMinerOutput:
    commits: List[RefactoringMinerCommit]


# TODO do we have such method anywhere
def get_full_github_url(author: str, repo: str) -> str:
    return f"https://github.com/{author}/{repo}"


class RefactoringMiner(Tool):
    def check_installed(self):
        pass

    def run(self, commit: Commit) -> RefactoringMinerOutput:
        url = get_full_github_url(commit.owner, commit.repository)
        cmd = ["./RefactoringMiner", "-gc", url, commit.sha, "1000"]

        result = subprocess.run(
            cmd, cwd=REFACTORING_MINER_PATH, capture_output=True, check=True
        )

        output = result.stdout.decode()
        return jsons.loads(output, cls=RefactoringMinerOutput)
