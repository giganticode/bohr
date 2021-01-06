import re
from typing import Optional, Tuple, Type

import requests
from cachetools import LRUCache
from snorkel.types import DataPoint

from bohr.artifacts.method import Method
from bohr.core import ArtifactMapper

regex = re.compile("git@github.com:(.*)/(.*).git")


def extract_owner_and_repo(repository_url: str) -> Tuple[str, str]:
    """
    >>> extract_owner_and_repo("git@github.com:apache/zookeeper.git")
    ('apache', 'zookeeper')
    """
    matcher = regex.match(repository_url)
    return matcher.group(1), matcher.group(2)


class MethodMapper(ArtifactMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__("MethodMapper", [], memoize=False)

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        owner, repository = extract_owner_and_repo(x.repository)
        url = f"https://raw.githubusercontent.com/{owner}/{repository}/{x.commit_hash}/{x.path}"
        text = requests.get(url).text
        text_lines = text.split("\n")

        def zero_based_line_number(l) -> int:
            return int(l) - 1

        start_line = zero_based_line_number(x.start_line)
        end_line = zero_based_line_number(x.end_line)
        needed_lines = text_lines[start_line : end_line + 1]

        key = (x.repository, x.commit_hash, x.path, start_line, end_line)
        if key in self.cache:
            return self.cache[key]

        method = Method("\n".join(needed_lines))
        self.cache[key] = method

        return method

    def get_artifact(self) -> Type:
        return Method
