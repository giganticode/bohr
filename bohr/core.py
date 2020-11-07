import importlib
import inspect
from pathlib import Path
from typing import List, Set, Callable

from snorkel.labeling import LabelingFunction, labeling_function

from bohr import HEURISTIC_DIR
from bohr.labels import Label
from bohr.snorkel_utils import CommitLabelingFunction

KEYWORD_GROUP_SEPARATOR = '|'


def load_keywords_from_file(path: Path) -> List[List[str]]:
    with open(path) as f:
        lines = f.readlines()
        return [line.rstrip('\n').split(KEYWORD_GROUP_SEPARATOR) for line in lines]


def load_labeling_functions(information_sources: Set[str]) -> List[LabelingFunction]:
    lfs = []
    for information_source in information_sources:
        module = importlib.import_module(f'bohr.heuristics.{information_source}')
        lfs.extend([obj for name, obj in inspect.getmembers(module)
                    if (isinstance(obj, LabelingFunction))])
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], LabelingFunction):
                lfs.extend(obj)

    return lfs


class keyword_labeling_functions(labeling_function):
    def __init__(self, keyword_list_name: str, name_pattern: str):
        super().__init__()
        file = HEURISTIC_DIR / 'keywords' / f'{keyword_list_name}.kwords'
        self.keyword_list = load_keywords_from_file(file)
        self.name_pattern = name_pattern

    def __call__(self, f: Callable[..., Label]) -> List[LabelingFunction]:
        function_list = []
        for keyword_group in self.keyword_list:
            def to_tuple_or_str(lst: List[str]): return lst[0] if len(lst) == 1 else tuple(lst)
            keywords = {to_tuple_or_str(kw.split(' ')) for kw in keyword_group}
            first_keyword = sorted(keywords, key=lambda x: "".join(x))[0]
            name_elem = first_keyword if isinstance(first_keyword, str) else '|'.join(first_keyword)
            name = self.name_pattern.replace('%1', name_elem)
            resources = dict(keywords=keyword_group)
            labeling_function = CommitLabelingFunction(name=name, f=lambda c, keywords: f(c, keywords).value, resources=resources)
            function_list.append(labeling_function)
        return function_list