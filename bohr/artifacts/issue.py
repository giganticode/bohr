from dataclasses import dataclass
from functools import cached_property
from typing import List, Set

from nltk import PorterStemmer, bigrams

from bohr.artifacts.core import Artifact
from bohr.nlp_utils import NgramSet, safe_tokenize


@dataclass
class Issue(Artifact):
    title: str
    body: str
    labels: List[str]

    @cached_property
    def stemmed_labels(self) -> Set[str]:
        stemmer = PorterStemmer()
        return {stemmer.stem(label) for label in self.labels}

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
