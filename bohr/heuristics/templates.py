import json
import re
from json.decoder import JSONDecodeError

from snorkel.labeling import LabelingFunction
import pandas as pd

from bohr.snorkel_utils import ABSTAIN, BUG, BUGLESS, Label, heuristic

COMMIT_MESSAGE_STEMMED = 'commit_message_stemmed'
ISSUE_CONTENTS_STEMMED = 'issue_contents_stemmed'
ISSUE_LABELS_STEMMED = 'issue_labels_stemmed'


def is_word_in_text(word: str, text: str) -> bool:
    """
    Examples:
    ---------
    >>> is_word_in_text("at", "cat is on the mat")
    False
    >>> is_word_in_text("cat", "cat is on the mat")
    True
    """
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)


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


@heuristic()
def fix_bugless__for_commit_message(x: pd.Series) -> Label:
    """
    #TODO I am really not convinced that fixing builds and JUnit tests are not bugfixes
    >>> fix_bugless__for_commit_message(pd.Series(data=['fix build'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> fix_bugless__for_commit_message(pd.Series(data=['JUnit test fix'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> fix_bugless__for_commit_message(pd.Series(data=['fix'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> fix_bugless__for_commit_message(pd.Series(data=['implementing new decoder'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    if is_word_in_text('fix', x.commit_message_stemmed.lower()):
        if any(is_word_in_text(word, x.commit_message_stemmed.lower()) for word in ['ad', 'add', 'build', 'chang', 'doc', 'document', 'javadoc', 'junit', 'messag', 'test', 'typo', 'unit', 'warn']):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN


@heuristic()
def bug_bugless__for_commit_message(x: pd.Series) -> Label:
    """
    >>> bug_bugless__for_commit_message(pd.Series(data=['doc bug'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> bug_bugless__for_commit_message(pd.Series(data=['fix bug in Javadoc'], index=[COMMIT_MESSAGE_STEMMED]))
    0
    >>> bug_bugless__for_commit_message(pd.Series(data=['bug'], index=[COMMIT_MESSAGE_STEMMED]))
    1
    >>> bug_bugless__for_commit_message(pd.Series(data=['implementing new decoder'], index=[COMMIT_MESSAGE_STEMMED]))
    -1
    """
    if is_word_in_text('bug', x.commit_message_stemmed.lower()):
        if any(is_word_in_text(word, x.commit_message_stemmed.lower()) for word in ['ad', 'add', 'chang', 'doc', 'document', 'javadoc', 'junit', 'report', 'test', 'typo', 'unit']):
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
    >>> s = pd.Series(data=['fix bug', 'defect'], index=[COMMIT_MESSAGE_STEMMED, ISSUE_LABELS_STEMMED])
    >>> keyword_lookup('fix', COMMIT_MESSAGE_STEMMED, BUG)(s)
    1
    >>> keyword_lookup('fi', COMMIT_MESSAGE_STEMMED, BUG)(s)
    -1
    >>> keyword_lookup('fi', COMMIT_MESSAGE_STEMMED, BUG, only_full_word=False)(s)
    1
    >>> keyword_lookup('fix', ISSUE_LABELS_STEMMED, BUG)(s)
    -1
    """
    @heuristic(name=f'{keyword}__for_{field}')
    def lf(x: pd.Series) -> Label:
        if x[field]:
            lowercased_field = str(x[field]).lower()
            if only_full_word:
                if is_word_in_text(keyword, lowercased_field):
                    return label
            elif keyword in lowercased_field:
                return label
        return ABSTAIN
    return lf
