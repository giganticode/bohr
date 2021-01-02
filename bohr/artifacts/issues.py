from dataclasses import dataclass
from functools import cached_property
from typing import List, Set

from nltk import PorterStemmer, bigrams

from bohr.nlp_utils import safe_tokenize, NgramSet


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
        if self.body is None:
            return set()
        return safe_tokenize(self.body)

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
            if not issue.stemmed_labels.isdisjoint(stemmed_labels):
                return True
        return False

    def match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        for issue in self.__issues:
            if not issue.stemmed_ngrams.isdisjoint(stemmed_keywords):
                return True
        return False
