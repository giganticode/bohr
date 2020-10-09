from enum import Enum
from functools import wraps, cached_property, lru_cache
from typing import Optional, List, Set, Mapping, Any, Tuple, Callable, Union
from snorkel.types import DataPoint

from bohr import TEST_DIR, TRAIN_DIR

from dataclasses import dataclass, field
from cachetools import LRUCache

import pandas as pd

import snorkel
from snorkel.labeling import labeling_function, LabelingFunction
from snorkel.preprocess import preprocessor, BasePreprocessor
from snorkel.map import BaseMapper, LambdaMapper
from snorkel.map.core import MapFunction

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
from nltk import bigrams


NgramSet = Set[Union[Tuple[str], str]]


class Label(Enum):
    BUG = 1
    BUGLESS = 0
    ABSTAIN = -1


def safe_word_tokenize(text: Any) -> Set[str]:
    if text is None: return set()
    if pd.isna(text): return set()

    return word_tokenize(str(text).lower())


@dataclass
class Issue:
    title: str
    body: str
    labels: List[str]

    @cached_property
    def stemmed_labels(self) -> Set[str]:
        stemmer = PorterStemmer()
        return set([stemmer.stem(l) for l in self.labels])

    @cached_property
    def tokens(self) -> Set[str]:
        if self.body is None: return set()
        return safe_word_tokenize(self.body)

    @cached_property
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stemmed_ngrams(self) -> NgramSet:
        return set(self.ordered_stems).union(set(bigrams(self.ordered_stems)))


class Issues:
    def __init__(self, issues):
        self.__issues = issues

    def __len__(self) -> int:
        return len(self.__issues)

    def __getitem__(self, idx) -> Issue:
        return self.__issues[idx]

    def match_label(self, stemmed_labels: Set[str]) -> bool:
        for issue in self.__issues:
            if not issue.stemmed_labels.isdisjoint(stemmed_labels): return True
        return False

    def match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        for issue in self.__issues:
            if not issue.stemmed_ngrams.isdisjoint(stemmed_keywords): return True
        return False



@dataclass
class CommitFile:
    filename: str
    status: str
    patch: Optional[str]
    changes: Optional[str]


class CommitFiles:
    def __init__(self, files):
        self.__files = files

    def __len__(self) -> int:
        return len(self.__files)

    def __getitem__(self, idx) -> CommitFile:
        return self.__files[idx]

@dataclass
class CommitMessage:
    raw: str

    @cached_property
    def tokens(self) -> Set[str]:
        if self.raw is None: return set()
        return safe_word_tokenize(self.raw)

    @cached_property
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stemmed_ngrams(self) -> NgramSet:
        return set(self.ordered_stems).union(set(bigrams(self.ordered_stems)))

    def match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        return not self.stemmed_ngrams.isdisjoint(stemmed_keywords)



@dataclass
class Commit:

    owner: str
    repository: str
    sha: str
    raw_message: str
    message: CommitMessage = field(init=False)

    def __post_init__(self):
        self.message = CommitMessage(self.raw_message)

    @lru_cache(maxsize=4)
    def __load_df(self, type: str, owner: str, repository: str):
        path = TRAIN_DIR / type  / owner / f"{repository}.csv"
        if path.is_file():
            return pd.read_csv(path, index_col=['sha'], keep_default_na=False, dtype={'labels': 'str'})
        else:
            return None

    def __hash__(self):
        return hash((self.owner, self.repository, self.sha))

    @cached_property
    def files(self) -> CommitFiles:
        df = self.__load_df('files', self.owner, self.repository)
        files = []

        if df is not None:
            try:
                df = df.loc[[self.sha]]
                for sha, file in df.iterrows():
                    files.append(CommitFile(file.filename, file.status, file.get('patch', None), file.get('change', None)))
            except KeyError as e:
                pass

        return CommitFiles(files)

    @cached_property
    def issues(self) -> Issues:
        df = self.__load_df('issues', self.owner, self.repository)
        issues = []

        if df is not None:
            try:
                df = df.loc[[self.sha]]
                for sha, issue in df.iterrows():
                    labels = issue.labels
                    labels = list(filter(None, labels.split(', ')))

                    issues.append(Issue(issue.title, issue.body, labels))
            except KeyError as e:
                pass

        return Issues(issues)

class CommitMapper(BaseMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__('CommitMapper', [], memoize=False)

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.owner, x.repository, x.sha)
        if key in self.cache:
            return self.cache[key]

        commit = Commit(x.owner, x.repository, x.sha, x.message)
        self.cache[key] = commit

        return commit


class CommitLabelingFunction(LabelingFunction):
    def __init__(
        self,
        name: str,
        f: Callable[..., int],
        resources: Optional[Mapping[str, Any]] = None,
        pre: Optional[List[BasePreprocessor]] = None,
    ) -> None:
        if pre is None:
            pre = []
        pre.insert(0, CommitMapper())            
        super().__init__(name, f, resources, pre=pre)


class commit_lf(labeling_function):
    def __call__(self, f: Callable[..., Label]) -> LabelingFunction:
        name = self.name or f.__name__
        return CommitLabelingFunction(name=name, f=lambda *args: f(*args).value, resources=self.resources, pre=self.pre)


def keywords_lookup_in_message(commit: Commit, keywords: NgramSet, label: Label) -> int:
    if commit.message.match_ngrams(keywords): return label.value
    return Label.ABSTAIN.value


def keywords_lookup_in_issue_label(commit: Commit, keywords: NgramSet, label: Label) -> int:
    if commit.issues.match_label(keywords): return label.value
    return Label.ABSTAIN.value


def keywords_lookup_in_issue_body(commit: Commit, keywords: NgramSet, label: Label) -> int:
    if commit.issues.match_ngrams(keywords): return label.value
    return Label.ABSTAIN.value


def keyword_lf(where: str, keyword_group: NgramSet, label: Label) -> CommitLabelingFunction:
    if not keyword_group:
        raise ValueError("At least one keyword needs to be provided")

    first_keyword = sorted(keyword_group, key=lambda x: "".join(x))[0]
    name_elem = first_keyword if isinstance(first_keyword, str) else '|'.join(first_keyword)

    name = f"{label.name.lower()}_{where}_keyword_{name_elem}"

    resources = dict(keywords=keyword_group, label=label)

    return CommitLabelingFunction(
        name=name,
        f=globals()[f"keywords_lookup_in_{where}"],
        resources=resources
    )


def keyword_lfs(keyword_list: List[Union[str, List[str]]], where: str, label: Label) -> List[LabelingFunction]:
    """
    >>> lfs = keyword_lfs(['keyword1', ['key word2', 'keyword3'], 'key word4'], 'message', Label.BUG)
    >>> lfs[0].name
    'bug_message_keyword_keyword1'
    >>> sorted(lfs[0]._resources['keywords'])
    ['keyword1']
    >>> lfs[1].name
    'bug_message_keyword_key|word2'
    >>> sorted(lfs[1]._resources['keywords'], key=lambda x: "".join(x))
    [('key', 'word2'), 'keyword3']
    >>> lfs[2].name
    'bug_message_keyword_key|word4'
    >>> sorted(lfs[2]._resources['keywords'])
    [('key', 'word4')]
    """
    lfs = []
    for keyword_group in keyword_list:
        if not (isinstance(keyword_group, str) or isinstance(keyword_group, list)):
            raise ValueError(f"Keyword or list of keywords expected, got: {keyword_group}")

        if isinstance(keyword_group, str):
            keyword_group = [keyword_group]

        def to_tuple_or_str(lst: List[str]): return lst[0] if len(lst) == 1 else tuple(lst)
        keywords = {to_tuple_or_str(kw.split(' ')) for kw in keyword_group}

        lfs.append(keyword_lf(where, keyword_group=keywords, label=label))

    return lfs
