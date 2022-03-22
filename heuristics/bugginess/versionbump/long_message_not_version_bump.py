# import re
# from typing import Optional
#
# import labels as l
# from bohrdev.collection.artifacts import Commit
# from bohrdev.collection.heuristictypes.keywords import KeywordHeuristics
# from bohrdev.core import Heuristic
# from bohrdev.labeling import Labels
# from bohrdev.util.misc import NgramSet
#
#
# @Heuristic(Commit)
# def long_message_not_version_bump(commit: Commit) -> Optional[Labels]:
#     if len(commit.message.raw) > 50:
#         return ~l.CommitLabel.VersionBump
#     else:
#         return None
#
# # TODO another heuristic: return ~l.CommitLabel.VersionBump if too many files changed
