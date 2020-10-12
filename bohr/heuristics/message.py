from bohr.core import keyword_labeling_functions
from bohr.snorkel_utils import commit_lf, Label, NgramSet
import re
from bohr.snorkel_utils import Commit


@keyword_labeling_functions('bug', name_pattern='bug_message_keyword_%1')
def bug_keywords_lookup_in_message(commit: Commit, keywords: NgramSet) -> Label:
    if commit.message.match_ngrams(keywords):
        return Label.BUG
    return Label.ABSTAIN


@keyword_labeling_functions('bugless', name_pattern='bugless_message_keyword_%1')
def bugless_keywords_lookup_in_message(commit: Commit, keywords: NgramSet) -> Label:
    if commit.message.match_ngrams(keywords):
        return Label.BUGLESS
    return Label.ABSTAIN


#@keyword_labeling_functions('bogusbugs', name_pattern='bogusbugs_message_keyword_%1')
def bogus_fix_keyword_in_message(commit: Commit, keywords: NgramSet) -> Label:
    if 'fix' in commit.message.stemmed_ngrams or 'bug' in commit.message.stemmed_ngrams:
        if commit.message.match_ngrams(keywords):
            return Label.BUGLESS
        else:
            return Label.BUG
    return Label.ABSTAIN


GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)
VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@commit_lf()
def github_ref_in_message(commit: Commit) -> Label:
    return Label.BUG if GITHUB_REF_RE.search(commit.message.raw) else Label.ABSTAIN


@commit_lf()
def version_in_message(commit: Commit) -> Label:
    return Label.BUGLESS if VERSION_RE.search(commit.message.raw) else Label.ABSTAIN

