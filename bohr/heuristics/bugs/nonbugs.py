from bohr.heuristics.templates import bug_bugless__for_commit_message, fix_bugless__for_commit_message, regex_version__for_commit_message, no_files_have_modified_status, keyword_lookup, COMMIT_MESSAGE_STEMMED, ISSUE_LABELS_STEMMED, ISSUE_CONTENTS_STEMMED
from bohr.snorkel_utils import BUGLESS

heuristics = [no_files_have_modified_status(BUGLESS)] + \
             [keyword_lookup(k, field=COMMIT_MESSAGE_STEMMED, label=BUGLESS) for k in [
                 'abil', 'ad', 'add', 'addit', 'allow', 'analysi', 'baselin', 'beautification', 'benchmark', 'better',
                 'chang log', 'clean', 'cleanup', 'comment', 'complet', 'configur chang', 'consolid', 'create',
                 'deprec', 'develop', 'doc', 'document', 'enhanc', 'exampl', 'exclud', 'extendgener', 'gitignor',
                 'implement', 'improv', 'includ', 'info', 'intorduc', 'javadoc', 'log', 'migrat', 'minim', 'move',
                 'new', 'note', 'opinion', 'optim', 'optimis', 'pass test', 'perf test', 'perfom test', 'perform',
                 'plugin', 'polish', 'prepar', 'provid', 'publish', 'readm', 'refactor', 'reformat', 'release',
                 'restructur', 'set up', 'simplif', 'simplifi', 'stage', 'stat', 'statist', 'support', 'switch',
                 'test coverag', 'test pass', 'todo', 'tweak', 'updat', 'upgrad', 'version']
              ] + \
             [keyword_lookup(k, field=ISSUE_LABELS_STEMMED, label=BUGLESS) for k in [
                 'ad', 'add', 'addit', 'build', 'bump', 'chang', 'check', 'cleanup', 'complet', 'deprec', 'do not',
                 'document', 'dont', 'enhanc', 'exampl', 'exclud', 'idea', 'implement', 'improv', 'info', 'junit',
                 'migrat', 'miss', 'modif', 'new', 'note', 'optim', 'perform', 'plugin', 'possibl', 'propos', 'provid',
                 'publish', 'readm', 'reduc', 'refactor', 'refin', 'reimplement', 'renam', 'reorgan', 'replac',
                 'restructur', 'review', 'rewrit', 'rid', 'speed up', 'speedup', 'todo', 'unit', 'updat']
              ] + \
             [keyword_lookup(k, field=ISSUE_CONTENTS_STEMMED, label=BUGLESS) for k in [
                 'abil', 'ad', 'add', 'addit', 'allow', 'analysi', 'avoid', 'baselin', 'benchmark', 'better', 'bump',
                 'chang log', 'cleanup', 'consolid', 'convert', 'create', 'deprec', 'develop', 'doc', 'document',
                 'drop', 'enhanc', 'exclud', 'expand', 'extendgener', 'forget', 'format', 'gitignor', 'idea',
                 'implement', 'improv', 'includ', 'intorduc', 'javadoc', 'limit', 'modif', 'move', 'new', 'note',
                 'opinion', 'optim', 'optimis', 'perform', 'plugin', 'polish', 'possibl', 'prepar', 'propos', 'provid',
                 'publish', 'readm', 'reduc', 'refactor', 'refin', 'regress test', 'reimplement', 'remov', 'renam',
                 'reorgan', 'replac', 'restrict', 'restructur', 'review', 'rewrit', 'rid', 'set up', 'simplif',
                 'simplifi', 'speed up', 'speedup', 'statist', 'support', 'test coverag', 'todo', 'tweak', 'unit',
                 'unnecessari', 'updat', 'upgrad', 'use']
              ] + [
                 keyword_lookup('featur', field=COMMIT_MESSAGE_STEMMED, label=BUGLESS, only_full_word=False),
                 keyword_lookup('featur', field=ISSUE_LABELS_STEMMED, label=BUGLESS, only_full_word=False),
                 keyword_lookup('featur', field=ISSUE_CONTENTS_STEMMED, label=BUGLESS, only_full_word=False),
                 bug_bugless__for_commit_message,
                 fix_bugless__for_commit_message,
                 regex_version__for_commit_message
             ]
