from bohr.heuristics.templates import regex_git2__for_commit_message, keyword_lookup, COMMIT_MESSAGE_STEMMED, ISSUE_LABELS_STEMMED, ISSUE_CONTENTS_STEMMED
from bohr.snorkel_utils import BUG

heuristics = [regex_git2__for_commit_message] + \
             [keyword_lookup(k, field=COMMIT_MESSAGE_STEMMED, label=BUG) for k in [
                 'bad', 'broken', 'bugg', 'concurr', 'correct', 'correctli', 'corrupt', 'crash', 'dead lock',
                 'deadlock', 'defect', 'endless', 'ensur', 'error', 'fail', 'failur', 'fix', 'fix and test', 'garbag',
                 'hotfix', 'incomplet', 'inconsist', 'incorrect', 'infinit', 'invalid', 'issue', 'leak', 'loop',
                 'mistak', 'not return', 'not work', 'prevent', 'problem', 'properli', 'quickfix', 'race condit',
                 'repair', 'small fix', 'solv', 'threw', 'throw', 'timeout', 'unabl', 'unclos', 'unexpect', 'unknown',
                 'unsynchron', 'wrong']
              ] + \
             [keyword_lookup(k, field=ISSUE_LABELS_STEMMED, label=BUG) for k in [
                 'bad', 'broken', 'bug', 'bugg', 'close', 'concurr', 'correct', 'crash', 'defect', 'error', 'fail',
                 'failur', 'fault', 'fix', 'handl', 'hotfix', 'invalid', 'issue', 'logic', 'merg', 'minor', 'quickfix',
                 'unknown']
              ] + \
             [keyword_lookup(k, field=ISSUE_CONTENTS_STEMMED, label=BUG) for k in [
                 'bad', 'broken', 'bug', 'bugg', 'close', 'concurr', 'correct', 'correctli', 'corrupt', 'crash',
                 'dead lock', 'deadlock', 'defect', 'disabl', 'endless', 'ensur', 'error', 'fail', 'failur',
                 'fault', 'fix', 'fix & test', 'fix and test', 'garbag', 'handl', 'hotfix', 'incomplet', 'inconsist',
                 'incorrect', 'infinit', 'invalid', 'issue', 'leak', 'loop', 'minor', 'mistak', 'not log', 'not return',
                 'not work', 'patch', 'prevent', 'problem', 'properli', 'quickfix', 'race condit', 'repair', 'resolv',
                 'small fix', 'solv', 'threw', 'throw', 'timeout', 'unabl', 'unclos', 'unexpect', 'unknown',
                 'unsynchron', 'wrong']] + \
             [keyword_lookup(k, field=COMMIT_MESSAGE_STEMMED, label=BUG, only_full_word=False) for k in [
                 'except', 'nullpointer', 'null pointer', 'outofbound', 'out of bound']
              ] + \
             [keyword_lookup(k, field=ISSUE_LABELS_STEMMED, label=BUG, only_full_word=False) for k in ['except']] + \
             [keyword_lookup(k, field=ISSUE_CONTENTS_STEMMED, label=BUG, only_full_word=False) for k in [
                 'except', 'nullpointer', 'null pointer', 'outofbound', 'out of bound']
              ]
