from bohr.core import keyword_labeling_functions
from bohr.nlp_utils import NgramSet
from bohr.labels import Label
from bohr.snorkel_utils import commit_lf
import re
from bohr.artifacts.commits import Commit


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


@commit_lf()
def no_files_have_modified_status(commit: Commit) -> Label:
    for file in commit.files:
        if file.status == 'modified': return Label.ABSTAIN
    return Label.BUGLESS


@commit_lf()
def bug_if_only_changed_lines_in_one_file(commit: Commit) -> Label:
    if len(commit.files) == 1 and commit.files[0].status == 'modified' \
            and commit.files[0].changes and commit.files[0].no_added_lines() and commit.files[0].no_removed_lines():
        return Label.BUG
    return Label.ABSTAIN


@commit_lf()
def bugless_if_many_files_changes(commit: Commit) -> Label:
    if len(commit.files) > 6:
        return Label.BUGLESS
    else:
        return Label.ABSTAIN
