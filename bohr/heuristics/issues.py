from bohr.core import keyword_labeling_functions
from bohr.snorkel_utils import Commit, NgramSet, Label


@keyword_labeling_functions('bug.issue_label', name_pattern='bug_issue_label_keyword_%1')
def bug_keywords_lookup_in_issue_label(commit: Commit, keywords: NgramSet) -> Label:
    if commit.issues.match_label(keywords):
        return Label.BUG
    return Label.ABSTAIN


@keyword_labeling_functions('bugless.issue_label', name_pattern='bugless_issue_label_keyword_%1')
def bugless_keywords_lookup_in_issue_label(commit: Commit, keywords: NgramSet) -> Label:
    if commit.issues.match_label(keywords):
        return Label.BUGLESS
    return Label.ABSTAIN


@keyword_labeling_functions('bug', name_pattern='bug_issue_body_keyword_%1')
def bug_keywords_lookup_in_issue_body(commit: Commit, keywords: NgramSet) -> Label:
    if commit.issues.match_ngrams(keywords):
        return Label.BUG
    return Label.ABSTAIN


@keyword_labeling_functions('bugless', name_pattern='bugless_issue_body_keyword_%1')
def bugless_keywords_lookup_in_issue_body(commit: Commit, keywords: NgramSet) -> Label:
    if commit.issues.match_ngrams(keywords):
        return Label.BUGLESS
    return Label.ABSTAIN