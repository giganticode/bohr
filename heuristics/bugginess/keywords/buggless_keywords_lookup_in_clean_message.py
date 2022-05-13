from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        "abil",
        "ad",
        "add",
        "addit",
        "allow",
        "analysi",
        "avoid",
        "baselin",
        "benchmark",
        "better",
        "chang log",
        ["clean", "cleanup"],
        "comment",
        "complet",
        "configur chang",
        "consolid",
        "convert",
        "coverag",
        "create",
        "deprec",
        "develop",
        ["doc", "document", "javadoc"],
        "drop",
        "enhanc",
        "exampl",
        "exclud",
        "expand",
        "extendgener",
        "featur",
        "forget",
        "gitignor",
        "idea",
        "implement",
        "improv",
        "includ",
        "info",
        "intorduc",
        "limit",
        "log",
        "migrat",
        "minim",
        "modif",
        "move",
        "new",
        "note",
        "opinion",
        ["optim", "optimis"],
        "pass test",
        "perf test",
        "perfom test",
        "perform",
        "plugin",
        "polish",
        "possibl",
        "prepar",
        "propos",
        "provid",
        "publish",
        "readm",
        "reduc",
        "refactor",
        "refin",
        "regress test",
        "reimplement",
        "remov",
        "renam",
        "reorgan",
        "replac",
        "restrict",
        "restructur",
        "review",
        "rewrit",
        "rid",
        "set up",
        "simplif",
        "simplifi",
        ["speedup", "speed up"],
        "stage",
        "stat",
        "statist",
        "support",
        "switch",
        "test",
        "test coverag",
        "test pass",
        "todo",
        "tweak",
        "unit",
        "unnecessari",
    ],
    name_pattern="bugless_clean_message_keyword_%1",
)
def bugless_keywords_lookup_in_clean_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    """
    >>> from types import SimpleNamespace
    >>> res = bugless_keywords_lookup_in_clean_message((Commit({"message": "MaxCount not working correctly in user/group query when"})), {"clean"})
    >>> res is None
    True
    """
    if commit.clean_message.match_ngrams(keywords):
        return CommitLabel.NonBugFix
    return None
