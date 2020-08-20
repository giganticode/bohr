# from bohr.heuristics.templates
from bohr.snorkel_utils import BUG, BUGLESS, ABSTAIN, commit_lf
import re
from bohr.snorkel_utils import Commit

BUG_MESSAGE_KEYWORDS = set([
    'bad', 'broken', 'bug', 'bugg', 'concurr', 'correct', 'correctli', 'corrupt', 'crash', 
   'deadlock', 'defect', 'endless', 'ensur', 'error', 'fail', 'failur', 'fix', 'garbag',
   'hotfix', 'incomplet', 'inconsist', 'incorrect', 'infinit', 'invalid', 'issue', 'leak', 'loop',
   'mistak', 'prevent', 'problem', 'properli', 'quickfix', 
   'repair', 'solv', 'threw', 'throw', 'timeout', 'unabl', 'unclos', 'unexpect', 'unknown',
   'unsynchron', 'wrong', 'except', 'nullpointer', 'outofbound', 'npe'
])

BUG_BIGRAMS = set([
    ('dead', 'lock'),
    ('not', 'work'),
    ('not', 'return'),
    ('small', 'fix'),
    ('race', 'condit'),
    ('of', 'bound'),
    ('null', 'pointer'),

])

BUG_ISSUE_LABEL_KEYWORDS = set([
    'bad', 'broken', 'bug', 'bugg', 'close', 'concurr', 'correct', 'crash', 'defect', 'error', 'fail',
    'failur', 'fault', 'fix', 'handl', 'hotfix', 'invalid', 'issue', 'logic', 'merg', 'minor', 'quickfix',
    'unknown'])

BUG_ISSUE_BODY_KEYWORDS = set([
    'bad', 'broken', 'bug', 'bugg', 'close', 'concurr', 'correct', 'correctli', 'corrupt', 'crash',
    'dead lock', 'deadlock', 'defect', 'disabl', 'endless', 'ensur', 'error', 'fail', 'failur',
    'fault', 'fix', 'garbag', 'handl', 'hotfix', 'incomplet', 'inconsist',
    'incorrect', 'infinit', 'invalid', 'issue', 'leak', 'loop', 'minor', 'mistak',
    'patch', 'prevent', 'problem', 'properli', 'quickfix', 'repair', 'resolv',
    'solv', 'threw', 'throw', 'timeout', 'unabl', 'unclos', 'unexpect', 'unknown',
    'unsynchron', 'wrong', 'except', 'nullpointer', 'outofbound', 'npe'])


BOGUS_FIX_KEYWORDS = set(["ad", "add", "build", "chang", "doc", "document",
                          "javadoc", "junit", "messag", "report", "test", "typo", "unit", "warn"])

NO_BUG_MESSAGE_KEYWORDS = set([
    'abil', 'ad', 'add', 'addit', 'allow', 'analysi', 'baselin', 'beautification', 'benchmark', 'better',
    'chang log', 'clean', 'cleanup', 'comment', 'complet', 'configur chang', 'consolid', 'create',
    'deprec', 'develop', 'doc', 'document', 'enhanc', 'exampl', 'exclud', 'extendgener', 'gitignor',
    'implement', 'improv', 'includ', 'info', 'intorduc', 'javadoc', 'log', 'migrat', 'minim', 'move',
    'new', 'note', 'opinion', 'optim', 'optimis', 'pass test', 'perf test', 'perfom test', 'perform',
    'plugin', 'polish', 'prepar', 'provid', 'publish', 'readm', 'refactor', 'reformat', 'release',
    'restructur', 'set up', 'simplif', 'simplifi', 'stage', 'stat', 'statist', 'support', 'switch',
    'test coverag', 'test pass', 'todo', 'tweak', 'updat', 'upgrad', 'version', 'featur'
])

NO_BUG_ISSUE_LABEL_KEYWORDS = set([
    'ad', 'add', 'addit', 'build', 'bump', 'chang', 'check', 'cleanup', 'complet', 'deprec', 'do not',
    'document', 'dont', 'enhanc', 'exampl', 'exclud', 'idea', 'implement', 'improv', 'info', 'junit',
    'migrat', 'miss', 'modif', 'new', 'note', 'optim', 'perform', 'plugin', 'possibl', 'propos', 'provid',
    'publish', 'readm', 'reduc', 'refactor', 'refin', 'reimplement', 'renam', 'reorgan', 'replac',
    'restructur', 'review', 'rewrit', 'rid', 'speed up', 'speedup', 'todo', 'unit', 'updat', 'featur'
])

NO_BUG_ISSUE_BODY_KEYWORDS = set([
    'abil', 'ad', 'add', 'addit', 'allow', 'analysi', 'avoid', 'baselin', 'benchmark', 'better', 'bump',
    'cleanup', 'consolid', 'convert', 'create', 'deprec', 'develop', 'doc', 'document',
    'drop', 'enhanc', 'exclud', 'expand', 'extendgener', 'forget', 'format', 'gitignor', 'idea',
    'implement', 'improv', 'includ', 'intorduc', 'javadoc', 'limit', 'modif', 'move', 'new', 'note',
    'opinion', 'optim', 'optimis', 'perform', 'plugin', 'polish', 'possibl', 'prepar', 'propos', 'provid',
    'publish', 'readm', 'reduc', 'refactor', 'refin', 'reimplement', 'remov', 'renam',
    'reorgan', 'replac', 'restrict', 'restructur', 'review', 'rewrit', 'rid', 'simplif',
    'simplifi', 'speedup', 'statist', 'support', 'test', 'coverag', 'todo', 'tweak', 'unit',
    'unnecessari', 'updat', 'upgrad', 'use', 'featur'])

NO_BUG_BIGRAMS = set([
    ('regress', 'test'),
    ('set', 'up'),
    ('chang', 'log'),
    ('speed', 'up'),
])

GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)
VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@commit_lf()
def github_ref_in_message(commit):
    return BUG if GITHUB_REF_RE.search(commit.message.raw) else ABSTAIN

@commit_lf()
def version_in_message(commit):
    return BUGLESS if VERSION_RE.search(commit.message.raw) else ABSTAIN

@commit_lf()
def bogus_fix_keyword_in_message(commit: Commit):
    if 'fix' in commit.message.stems or 'bug' in commit.message.stems:
        if commit.message.match(BOGUS_FIX_KEYWORDS):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN



@commit_lf()
def bug_keyword_in_message(commit):
    if commit.message.match(BUG_MESSAGE_KEYWORDS): return BUG
    if commit.message.match_bigram(BUG_BIGRAMS): return BUG
    return ABSTAIN

@commit_lf()
def no_bug_keyword_in_message(commit):
    return BUGLESS if commit.message.match(NO_BUG_MESSAGE_KEYWORDS) else ABSTAIN



@commit_lf()
def bug_keyword_in_issue_labels(commit):
    return BUG if commit.issues.match_label(BUG_ISSUE_LABEL_KEYWORDS) else ABSTAIN

@commit_lf()
def no_bug_keyword_in_issue_labels(commit):
    return BUGLESS if commit.issues.match_label(NO_BUG_ISSUE_LABEL_KEYWORDS) else ABSTAIN



@commit_lf()
def bug_keyword_in_issues(commit: Commit):
    if commit.issues.match(BUG_ISSUE_BODY_KEYWORDS): return BUG
    if commit.issues.match_bigram(BUG_BIGRAMS): return BUG

    return ABSTAIN

@commit_lf()
def no_bug_keyword_in_issues(commit: Commit):
    if commit.issues.match(NO_BUG_ISSUE_BODY_KEYWORDS): return BUGLESS
    if commit.issues.match_bigram(NO_BUG_BIGRAMS): return BUGLESS

    return ABSTAIN



@commit_lf()
def no_files_have_modified_status(commit: Commit):
    for file in commit.files:
        if file.status == 'modified': return ABSTAIN
        if file.status == 'added': return ABSTAIN
    return BUGLESS        
