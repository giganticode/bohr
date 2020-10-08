from bohr.snorkel_utils import BUG, BUGLESS, ABSTAIN, commit_lf, keyword_lfs
import re
from bohr.snorkel_utils import Commit

BUG_MESSAGE_KEYWORDS = [
    'bad',
    'broken',
    ['bug', 'bugg'],
    'close',
    'concurr',
    ['correct', 'correctli'],
    'corrupt',
    'crash',
    ['deadlock', 'dead lock'],
    'defect',
    'disabl',
    'endless',
    'ensur',
    'error',
    'except',
    ['fail', 'failur', 'fault'],
    ['fix', 'hotfix', 'quickfix', 'small fix'],
    'garbag',
    'handl',
    'incomplet',
    'inconsist',
    'incorrect',
    'infinit',
    'invalid',
    'issue',
    'leak',
    'loop',
    'minor',
    'mistak',
    ['nullpointer', 'npe', 'null pointer'],
    'not work',
    'not return',
    ['outofbound', 'of bound'],
    'patch',
    'prevent',
    'problem',
    'properli',
    'race condit',
    'repair',
    ['resolv', 'solv'],
    ['threw', 'throw'],
    'timeout',
    'unabl',
    'unclos',
    'unexpect',
    'unknown',
    'unsynchron',
    'wrong',
]


NO_BUG_MESSAGE_KEYWORDS = [
   'abil',
   'ad',
   'add',
   'addit',
   'allow',
   'analysi',
   'avoid',
   'baselin',
   'beautification',
   'benchmark',
   'better',
   'bump',
   'chang log',
   ['clean', 'cleanup'],
   'comment',
   'complet',
   'configur chang',
   'consolid',
   'convert',
   'coverag',
   'create',
   'deprec',
   'develop',
   ['doc', 'document', 'javadoc'],
   'drop',
   'enhanc',
   'exampl',
   'exclud',
   'expand',
   'extendgener',
   'featur',
   'forget',
   'format',
   'gitignor',
   'idea',
   'implement',
   'improv',
   'includ',
   'info',
   'intorduc',
   'javadoc',
   'limit',
   'log',
   'migrat',
   'minim',
   'modif',
   'move',
   'new',
   'note',
   'opinion',
   ['optim', 'optimis'],
   'pass test',
   'perf test',
   'perfom test',
   'perform',
   'plugin',
   'polish',
   'possibl',
   'prepar',
   'propos',
   'provid',
   'publish',
   'readm',
   'reduc',
   'refactor',
   'refin',
   'reformat',
   'regress test',
   'reimplement',
   'release',
   'remov',
   'renam',
   'reorgan',
   'replac',
   'restrict',
   'restructur',
   'review',
   'rewrit',
   'rid',
   'set up',
   'simplif',
   'simplifi',
   ['speedup', 'speed up'],
   'stage',
   'stat',
   'statist',
   'support',
   'switch',
   'test',
   'test coverag',
   'test pass',
   'todo',
   'tweak',
   'unit',
   'unnecessari',
   'updat',
   'upgrad',
   'version'
]


BUG_ISSUE_LABEL_KEYWORDS = [
    'bug',
    'fixed',
    'fix',
    'error'
]

NO_BUG_ISSUE_LABEL_KEYWORDS = [
    'enhancement',
    'feature',
    'request',
    'refactor',
    'renovate',
    'new',

]

BOGUS_FIX_KEYWORDS = set(["ad", "add", "build", "chang", "doc", "document",
                          "javadoc", "junit", "messag", "report", "test", "typo", "unit", "warn"])


GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)
VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@commit_lf()
def github_ref_in_message(commit):
    return BUG if GITHUB_REF_RE.search(commit.message.raw) else ABSTAIN

@commit_lf()
def version_in_message(commit):
    return BUGLESS if VERSION_RE.search(commit.message.raw) else ABSTAIN

#@commit_lf()
def bogus_fix_keyword_in_message(commit: Commit):
    if 'fix' in commit.message.stems or 'bug' in commit.message.stems:
        if commit.message.match(BOGUS_FIX_KEYWORDS):
            return BUGLESS
        else:
            return BUG
    return ABSTAIN

#@commit_lf()
def no_files_have_modified_status(commit: Commit):
    for file in commit.files:
        if file.status == 'modified': return ABSTAIN
        if file.status == 'added': return ABSTAIN
    return BUGLESS

