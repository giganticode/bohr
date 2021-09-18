# import re
# from typing import Optional, Dict
#
# import jsons
# import pycoshark
# from bohr.labeling.labelset import Labels
# from mongoengine import connect, DoesNotExist
# from pycoshark.mongomodels import Project, VCSSystem, Commit, FileAction, Hunk, Refactoring, IssueSystem, Issue, \
#     IssueComment, MailingList, Message, Branch
# from pycoshark.utils import create_mongodb_uri_string
# from bohr.core import Heuristic
# from bohr.collection.artifacts import Commit as C
#
# import labels as l
#
#
# # You may have to update this dict to match your DB credentials
#
# credentials = {'db_user': '',
#                'db_password': '',
#                'db_hostname': '10.10.20.160',
#                'db_port': 27017,
#                'db_authentication_database': '',
#                'db_ssl_enabled': False}
#
# uri = create_mongodb_uri_string(**credentials)
#
# connect('smartshark_1_2', host=uri, alias='default')
#
#
# def get_smartshark_data(sha: str) -> Dict:
#     fields_to_get = ['id', 'vcs_system_id', 'revision_hash', 'branches', 'parents', 'author_id', 'author_date', 'author_date_offset', 'committer_id', 'committer_date', 'committer_date_offset', 'message', 'linked_issue_ids', 'code_entity_states', 'labels', 'validations', 'fixed_issue_ids', 'szz_issue_ids']
#     commit = Commit.objects(revision_hash=sha).get()
#     commit_dict = {key: getattr(commit, key) for key in fields_to_get}
#     branch_name = Branch.objects(commit_id=commit.id).get().name
#     commit_dict['branch_name'] = branch_name
#     return commit_dict
#
#
# @Heuristic(C)
# def smartshark(commit: C) -> Optional[Labels]:
#     try:
#         get_smartshark_data(commit.sha)
#         return l.CommitLabel.BugFix
#     except DoesNotExist:
#         return None
#
#
# d = get_smartshark_data('08e02602e947ff945b9bd73ab5f0b45863df3e53')
# print(d)
#
#
#
# # {'adjustedszz_bugfix': False, 'issueonly_bugfix': False, 'testchange_javacode': False, 'documentation_technicaldept_add': False, 'refactoring_codebased': False, 'documentation_technicaldept_remove': False, 'refactoring_keyword': False, 'documentation_javainline': True, 'documentation_javadoc': True, 'issueonly_featureadd': False, 'validated_bugfix': False}
# # ['id', 'vcs_system_id', 'revision_hash', 'branches', 'parents', 'author_id', 'author_date', 'author_date_offset', 'committer_id', 'committer_date', 'committer_date_offset', 'message', 'linked_issue_ids', 'code_entity_states', 'labels', 'validations', 'fixed_issue_ids', 'szz_issue_ids']
# # ['id', 'vcs_system_id', 'revision_hash', 'branches', 'parents', 'author_id', 'author_date', 'author_date_offset', 'committer_id', 'committer_date', 'committer_date_offset', 'message', 'linked_issue_ids', 'code_entity_states', 'labels', 'validations', 'fixed_issue_ids', 'szz_issue_ids']
