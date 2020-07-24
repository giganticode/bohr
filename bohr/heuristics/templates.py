import json
import re
from json.decoder import JSONDecodeError
from typing import List, Optional, Callable

from snorkel.labeling import labeling_function, LabelingFunction
import pandas as pd

from bohr.snorkel_utils import ABSTAIN, BUG, BUGLESS, LABEL

COMMIT_MESSAGE = 'commit_message'
ISSUE_CONTENTS = 'issue_contents'
ISSUE_LABELS = 'issue_labels'


def is_word_in_text(word, text) -> bool:
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


def keyword_lookup(x: pd.DataFrame, keyword: str, field: str, label: LABEL, only_full_word=True) -> LABEL:
    """
    Examples:
    ---------
    >>> s = pd.Series(data=['fix bug', 'defect'], index=[COMMIT_MESSAGE, ISSUE_LABELS])
    >>> keyword_lookup(s, 'fix', COMMIT_MESSAGE, BUG)
    1
    >>> keyword_lookup(s, 'fi', COMMIT_MESSAGE, BUG)
    -1
    >>> keyword_lookup(s, 'fi', COMMIT_MESSAGE, BUG, only_full_word=False)
    1
    >>> keyword_lookup(s, 'fix', ISSUE_LABELS, BUG)
    -1
    """
    if x[field]:
        lowercased_field = str(x[field]).lower()
        if only_full_word:
            if is_word_in_text(keyword, lowercased_field):
                return label
        elif keyword in lowercased_field:
            return label
    return ABSTAIN


def keyword_lookup_template(terms: List[str], label: int, restrict_to_fields: Optional[List[str]] = None, only_full_word=True) -> List[Callable]:
    restrict_to_fields = restrict_to_fields or [COMMIT_MESSAGE, ISSUE_CONTENTS, ISSUE_LABELS]

    labeling_functions = []
    for term in terms:
        for field in restrict_to_fields:
            labeling_functions.append(LabelingFunction(
                name= f'{term}__for_{field}',
                f=keyword_lookup,
                resources=dict(keyword=term, field=f'{field}_stemmed', label=label, only_full_word=only_full_word)
            ))
    return labeling_functions


@labeling_function()
def regex_git2__for_commit_message(x: pd.Series):
    return BUG if re.search(r"gh(-|\s)\d+", x.commit_message_stemmed, flags=re.I) else ABSTAIN


@labeling_function()
def regex_version__for_commit_message(x):
    return BUGLESS if re.search(r"v\d+.*", x.commit_message_stemmed, flags=re.I) else ABSTAIN


@labeling_function()
def fix_bugless__for_commit_message(x):
    if is_word_in_text('fix', x.commit_message_stemmed.lower()):
        if any(is_word_in_text(word, x.commit_message_stemmed.lower()) for word in ['ad', 'add', 'build', 'chang', 'doc', 'document', 'javadoc', 'junit', 'messag', 'test', 'typo', 'unit', 'warn']):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN


@labeling_function()
def bug_bugless__for_commit_message(x):
    if is_word_in_text('bug', x.commit_message_stemmed.lower()):
        if any(is_word_in_text(word, x.commit_message_stemmed.lower()) for word in ['ad', 'add', 'chang', 'doc', 'document', 'javadoc', 'junit', 'report', 'test', 'typo', 'unit']):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN


@labeling_function()
def no_files_have_modified_status(x) -> bool:
    try:
        for file in json.loads(x.file_details):
            if file['status'] == 'modified':
                return ABSTAIN
        return BUGLESS
    except JSONDecodeError:
        return ABSTAIN

