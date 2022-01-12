from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        ["beautification", 'create', "extendgener", "intorduc", "perfom test", "release", "configur chang", "opinion", "pass test", "perf test",
         "simplif", "baselin", "reimplement", "forget", "consolid", "chang log", "polish", "test pass", "speedup", "speed up", "test coverag",
         "reorgan", "statist", "regress test", "minim", "propos", "restructur", "refin", "reformat", "benchmark", "set up", "analysi", "idea",
         "restrict", "modif", "rid", "exclud", "stage" "rewrit", "expand", "stat", "coverag", "todo", "reduc", "gitignor", "abil",
         "enhanc", "limit", "perform", "unnecessari", "tweak", "drop", "optim", "optimis", "simplifi", "deprec", "convert"],
        ["migrat", "addit", "complet", "publish", "possibl", "prepar", "switch", "info", "unit", "upgrad", "provid", "better", "note", "avoid", "replac"],
        ["format", "exampl", "plugin", "renam", "comment", "includ", "develop", "bump", "log"],
        ["review", "improv", "implement", "featur", "refactor", "allow"],
        ["clean", "cleanup", "move", "readm", "support"],
        ["doc", "document", "javadoc", "new", "version"],
        ["remov"],
        ["test"],
        ["ad", "add"],
        ["updat"]
    ],
    name_pattern="bugless_message_keyword_combined_%1",
)
def bugless_keywords_lookup_in_message_combined(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.NonBugFix
    return None
