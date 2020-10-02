import json
import re
from json.decoder import JSONDecodeError
from typing import List

from snorkel.labeling import LabelingFunction
import pandas as pd

from bohr.heuristics.preprocessors import lowercase, tokenize, get_field_extractor
from bohr.snorkel_utils import ABSTAIN, BUG, BUGLESS, Label, text_lf

COMMIT_MESSAGE_STEMMED = 'commit_message_stemmed'
ISSUE_CONTENTS_STEMMED = 'issue_contents_stemmed'
ISSUE_LABELS_STEMMED = 'issue_labels_stemmed'


# def is_sublist(sublist: List[str], lst: List[str]) -> bool:
#     """
#     >>> is_sublist([], ['cat', 'is', 'on'])
#     True
#     >>> is_sublist(['is'], ['cat', 'is'])
#     True
#     >>> is_sublist(['cat', 'is'], ['cat', 'is'])
#     True
#     >>> is_sublist(['is', 'on'], ['cat', 'is', 'on'])
#     True
#     >>> is_sublist(['cat', 'is'], ['cat', 'on'])
#     False
#     >>> is_sublist(['cat', 'is'], ['cat'])
#     False
#     """
#     if len(sublist) == 0:
#         return True

#     try:
#         first_index = lst.index(sublist[0])
#         for i in range(1, len(sublist)):
#             if lst[first_index + i] != sublist[i]:
#                 return False
#         return True
#     except (ValueError, IndexError):
#         return False





# def no_files_have_modified_status(label: Label) -> LabelingFunction:
#     """
#     >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[]'], index=['file_details']))
#     0
#     >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "added"}]'], index=['file_details']))
#     0
#     >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "modified"}]'], index=['file_details']))
#     -1
#     >>> no_files_have_modified_status(BUGLESS)(pd.Series(data=['[{"status": "modified"}, {"status": "added"}]'], \
# index=['file_details']))
#     -1
#     """

#     @heuristic(name='no_files_have_modified_status')
#     def lf(x: pd.Series) -> Label:
#         try:
#             for file in json.loads(x.file_details):
#                 if file['status'] == 'modified':
#                     return ABSTAIN
#             return label
#         except JSONDecodeError:
#             return ABSTAIN

#     return lf




