import inspect

from snorkel.labeling import LabelingFunction

from bohr.heuristics.bug import BUG_MESSAGE_KEYWORDS, BUG_ISSUE_LABEL_KEYWORDS, NO_BUG_MESSAGE_KEYWORDS, \
    NO_BUG_ISSUE_LABEL_KEYWORDS
from bohr.snorkel_utils import keyword_lfs, BUG, BUGLESS


def all_lfs(module):
    lfs = [obj for name, obj in inspect.getmembers(module) if (isinstance(obj, LabelingFunction))]

    keyword_labeling_functions = [
        *keyword_lfs(BUG_MESSAGE_KEYWORDS, 'message', BUG),
        *keyword_lfs(BUG_ISSUE_LABEL_KEYWORDS, 'issue_label', BUG),
        *keyword_lfs(BUG_MESSAGE_KEYWORDS, 'issue_body', BUG),

        *keyword_lfs(NO_BUG_MESSAGE_KEYWORDS, 'message', BUGLESS),
        *keyword_lfs(NO_BUG_ISSUE_LABEL_KEYWORDS, 'issue_label', BUGLESS),
        *keyword_lfs(NO_BUG_MESSAGE_KEYWORDS, 'issue_body', BUGLESS),
    ]
    lfs.extend(keyword_labeling_functions)
    return lfs
