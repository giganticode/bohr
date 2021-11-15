import re
from typing import List, Optional, Tuple

import spacy
from spacy.tokens import Token

import labels as l
from bohr.collection.artifacts import Commit
from bohr.collection.heuristictypes.keywords import KeywordHeuristics
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels
from bohr.util.misc import NgramSet
from heuristics import nlp


def verb_looking(s: Token) -> bool:
    if s.lemma_ == "bug":
        return False
    return s.text.endswith("es") or s.text.endswith("ed") or s.pos_ == "VERB"


SentenceCore = Tuple[Tuple[Optional[Token], Optional[Token]], str]
VERB_PHRASE = "verb_phrase"
NOUN_VERB_PHRASE = "noun_verb_phrase"
NOUN_PHRASE = "noun_phrase"


def get_sentence_core(sentence) -> SentenceCore:
    root_token = sentence.root
    children_list = [c for c in root_token.children]
    if verb_looking(root_token):
        for child in children_list:
            if child.dep_ in ["dobj", "nummod"]:
                return (root_token, child), VERB_PHRASE
            elif child.dep_ == "nsubj" and not verb_looking(child):
                return (root_token, child), NOUN_VERB_PHRASE
        return (
            root_token,
            children_list[0] if len(children_list) > 0 else None,
        ), "verb+?"
    else:
        for child in children_list:
            if (
                child.dep_ in ["amod", "nsubj", "compound"]
                and child.text == str(sentence[0])
                and verb_looking(child)
            ):
                return (child, root_token), "verb_phrase"
        return (
            root_token,
            children_list[0] if len(children_list) > 0 else None,
        ), NOUN_PHRASE


def get_lemma(token) -> str:
    return token.lemma_.lower() if token is not None else None


def get_commit_cores(s: str, model) -> List[SentenceCore]:
    """
    >>> get_commit_cores("fix some issues with code", nlp)
    [(('fix', 'issue'), 'verb_phrase')]
    >>> get_commit_cores("fixed tricky bug", nlp)
    [(('fix', 'bug'), 'verb_phrase')]
    >>> get_commit_cores("Fixes bug", nlp)
    [(('fix', 'bug'), 'verb_phrase')]
    >>> get_commit_cores("bug fix", nlp)
    [(('fix', 'bug'), 'noun_phrase')]
    >>> get_commit_cores("improvement", nlp)
    [(('improvement', None), 'noun_phrase')]
    """

    res = []
    s = s.rstrip("\n")
    doc = model(s)
    for sentence in doc.sents:
        sentence_core = get_sentence_core(sentence)
        res.append(
            (
                (get_lemma(sentence_core[0][0]), get_lemma(sentence_core[0][1])),
                sentence_core[1],
            )
        )
    return res


@Heuristic(Commit)
def verb_phrase_fix(commit: Commit) -> Optional[Labels]:
    lst = get_commit_cores(commit.message.raw, nlp)
    if len(lst) == 1:
        first_sentence_core = lst[0]
        phrase = first_sentence_core[0]
        phrase_type = first_sentence_core[1]
        if phrase_type in [VERB_PHRASE, NOUN_PHRASE]:
            if phrase[0] in ["fix", "correct"]:
                if phrase[1] in [
                    "test",
                    "javadoc",
                    "doc",
                    "unittest",
                    "warning",
                    "typo",
                ]:
                    return l.CommitLabel.NonBugFix
                else:
                    return l.CommitLabel.BugFix
    return None


# keywords from Towards automatic generation of short summaries of commits
@KeywordHeuristics(
    Commit,
    keywords=[
        "add",
        "create",
        "make",
        "implement",
        "remove",
        "update",
        "use",
        "move",
        "change",
        "prepare",
        "improve",
        "ignore",
        "handle",
        "rename",
        "allow",
        "set",
        "replace",
    ],
    name_pattern="verb_phrase_%1",
)
def verb_phrase_non_fix(commit: Commit, keyword: NgramSet) -> Optional[Labels]:
    lst = get_commit_cores(commit.message.raw, nlp)
    if len(lst) == 1:
        first_sentence_core = lst[0]
        phrase = first_sentence_core[0]
        phrase_type = first_sentence_core[1]
        if phrase_type == VERB_PHRASE:
            if phrase[0] == keyword:
                return l.CommitLabel.NonBugFix
    return None


@KeywordHeuristics(
    Commit,
    keywords=["implementation", "update", "change", "improvement", "handle"],
    name_pattern="noun_phrase_%1",
)
def noun_phrase_non_fix(commit: Commit, keyword: NgramSet) -> Optional[Labels]:
    lst = get_commit_cores(commit.message.raw, nlp)
    if len(lst) == 1:
        first_sentence_core = lst[0]
        phrase = first_sentence_core[0]
        phrase_type = first_sentence_core[1]
        if phrase_type == NOUN_PHRASE:
            if phrase[0] == keyword:
                return l.CommitLabel.NonBugFix
    return None
