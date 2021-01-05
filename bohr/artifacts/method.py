from dataclasses import dataclass
from functools import cached_property
from typing import List

from bohr.artifacts.core import Artifact


@dataclass
class Method(Artifact):
    _text: str

    @cached_property
    def lines(self) -> List[str]:
        return self._get_lines()

    @cached_property
    def max_depth(self) -> int:
        return self._get_max_depth()

    def _get_lines(self) -> List[str]:
        """
        >>> Method("public a() {}").lines
        ['public a() {}']
        """
        return self._text.split("\n")

    def _get_max_depth(self) -> int:
        """
        >>> Method("{}}").max_depth
        Traceback (most recent call last):
        ...
        ValueError: Invalid method text: {}}
        >>> Method("public a() {}").max_depth
        1
        >>> Method("public a() {if (true) {}}").max_depth
        2
        """
        level = 0
        max_level = level
        for char in self._text:
            if char == "{":
                level += 1
                if level > max_level:
                    max_level = level
            elif char == "}":
                level -= 1

            if level == -1:
                raise ValueError(f"Invalid method text: {self._text}")
        return max_level
