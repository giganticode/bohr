import json
import re
from json.decoder import JSONDecodeError
from typing import List

from snorkel.labeling import LabelingFunction
import pandas as pd

from bohr.heuristics.preprocessors import lowercase, tokenize, get_field_extractor
from bohr.snorkel_utils import ABSTAIN, BUG, BUGLESS, Label, heuristic

COMMIT_MESSAGE_STEMMED = 'commit_message_stemmed'
ISSUE_CONTENTS_STEMMED = 'issue_contents_stemmed'
ISSUE_LABELS_STEMMED = 'issue_labels_stemmed'


def is_sublist(sublist: List[str], lst: List[str]) -> bool:
    """
    >>> is_sublist([], ['cat', 'is', 'on'])
    True
    >>> is_sublist(['is'], ['cat', 'is'])
    True
    >>> is_sublist(['cat', 'is'], ['cat', 'is'])
    True
    >>> is_sublist(['is', 'on'], ['cat', 'is', 'on'])
    True
    >>> is_sublist(['cat', 'is'], ['cat', 'on'])
    False
    >>> is_sublist(['cat', 'is'], ['cat'])
    False
    """
    if len(sublist) == 0:
        return True

    try:
        first_index = lst.index(sublist[0])
        for i in range(1, len(sublist)):
            if lst[first_index + i] != sublist[i]:
                return False
        return True
    except (ValueError, IndexError):
        return False


@heuristic()
def regex_git2__for_commit_message(x: pd.Series) -> Label:
    """
    #TODO why do we make the assumption that all referenced issues are defects?
    >>> regex_git2__for_commit_message(pd.Series(data=['closes gh-17999'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> regex_git2__for_commit_message(pd.Series(data=['fixes gh 123'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> regex_git2__for_commit_message(pd.Series(data=['implements GH 123'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> regex_git2__for_commit_message(pd.Series(data=['message without issue reference'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    >>> regex_git2__for_commit_message(pd.Series(data=['wrong way to reference issue gh6567'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    return BUG if re.search(r"gh(-|\s)\d+", x.commit_message_stemmed, flags=re.I) else ABSTAIN


@heuristic()
def regex_version__for_commit_message(x: pd.Series) -> Label:
    """
    >>> regex_version__for_commit_message(pd.Series(data=['bump to v1.0.9'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> regex_version__for_commit_message(pd.Series(data=['bump to version 1.0.9'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    return BUGLESS if re.search(r"v\d+.*", x.commit_message_stemmed, flags=re.I) else ABSTAIN


@heuristic(pre=[get_field_extractor(COMMIT_MESSAGE_STEMMED), lowercase, tokenize])
def fix_bugless__for_commit_message(x: pd.Series) -> Label:
    """
    #TODO I am really not convinced that fixing builds and JUnit tests are not bugfixes
    >>> fix_bugless__for_commit_message(pd.Series(data=['fix build'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> fix_bugless__for_commit_message(pd.Series(data=['JUnit test fix'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> fix_bugless__for_commit_message(pd.Series(data=['fix Decorator building blocks'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> fix_bugless__for_commit_message(pd.Series(data=['implementing new decoder'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    if 'fix' in x:
        if any(is_sublist(word.split(), x) for word in ['ad', 'add', 'build', 'chang', 'doc', 'document', 'javadoc', 'junit', 'messag', 'test', 'typo', 'unit', 'warn']):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN


@heuristic(pre=[get_field_extractor(COMMIT_MESSAGE_STEMMED), lowercase, tokenize])
def bug_bugless__for_commit_message(x: pd.Series) -> Label:
    """
    >>> bug_bugless__for_commit_message(pd.Series(data=['doc bug'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> bug_bugless__for_commit_message(pd.Series(data=['fix bug in doc'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> bug_bugless__for_commit_message(pd.Series(data=['bug in docHelp method'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> bug_bugless__for_commit_message(pd.Series(data=['implementing new decoder'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    if 'bug' in x:
        if any(is_sublist(word.split(), x) for word in ['ad', 'add', 'chang', 'doc', 'document', 'javadoc', 'junit', 'report', 'test', 'typo', 'unit']):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN


def no_files_have_modified_status(label: Label) -> LabelingFunction:
    """
    >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[]'], index=['file_details']))
    0
    >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "added"}]'], index=['file_details']))
    0
    >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "modified"}]'], index=['file_details']))
    -1
    >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "modified"}, {"status": "added"}]'], \
index=['file_details']))
    -1
    """

    @heuristic(name='no_files_have_modified_status')
    def lf(x: pd.Series) -> Label:
        try:
            for file in json.loads(x.file_details):
                if file['status'] == 'modified':
                    return ABSTAIN
            return label
        except JSONDecodeError:
            return ABSTAIN

    return lf


def keyword_lookup(keyword: str, field: str, label: Label, only_full_word=True) -> LabelingFunction:
    """
    Examples:
    ---------
    >>> s = pd.Series(data=['Fix bug', 'defect'], index=[COMMIT_MESSAGE_STEMMED, ISSUE_LABELS_STEMMED])
    >>> keyword_lookup('fix', COMMIT_MESSAGE_STEMMED, BUG)(s)
    1
    >>> keyword_lookup('fi', COMMIT_MESSAGE_STEMMED, BUG)(s)
    -1
    >>> keyword_lookup('fix bu', COMMIT_MESSAGE_STEMMED, BUG, only_full_word=False)(s)
    1
    >>> keyword_lookup('fix', ISSUE_LABELS_STEMMED, BUG)(s)
    -1
    """
    @heuristic(name=f'{keyword}__for_{field}', pre=[get_field_extractor(field), lowercase])
    def lf(x: pd.Series) -> Label:
        if x:
            if only_full_word:
                if is_sublist(keyword.split(), x.split()):
                    return label
            elif keyword in x:
                return label
        return ABSTAIN
    return lf
