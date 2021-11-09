import re
from typing import List, Optional, Tuple

import labels as l
from bohr.collection.artifacts import Commit
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels
from bohr.util.misc import NgramSet
from heuristics import nlp


def verb_looking(s: str) -> bool:
    return s.endswith("es") or s.endswith("ed") or s == "fix"


def get_verb_noun_phrase(s: str) -> List[Tuple[str, str]]:
    res = []
    doc = nlp(s)
    for sentence in doc.sents:
        root_token = sentence.root
        verb = None
        obj = None
        tp = None
        children_list = [c for c in root_token.children]
        for child in children_list:
            if child.dep_ == "nsubj" and not verb_looking(child.text):
                verb = child
                obj = root_token
                tp = "noun_verb_phrase"
                break
            elif (
                child.dep_ in ["amod", "nsubj", "compound"]
                and child.text == str(sentence[0])
                and verb_looking(child.text)
            ):
                verb = child
                obj = root_token
                tp = "verb_phrase"
                break
            elif child.dep_ in ["dobj", "nummod"]:
                verb = root_token
                obj = child
                tp = "verb_phrase"
                break
        if verb is not None:
            res.append(((verb.lemma_, obj.lemma_), tp))
        else:
            dep = children_list[0] if len(children_list) > 0 else ""
            res.append(
                ((root_token.lemma_, dep.lemma_ if type(dep) != str else ""), "other")
            )
    return res


@Heuristic(Commit)
def sp(commit: Commit) -> Optional[Labels]:
    lst = get_verb_noun_phrase(commit.message.raw)
    if len(lst) == 1:
        phrase = lst[0][0]
        phrase_type = lst[0][1]
        if phrase_type == "verb_phrase":
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
            else:
                return l.CommitLabel.NonBugFix
    elif len(lst) >= 3:
        return l.CommitLabel.NonBugFix  # Tangled
