N_PARALLEL = 1
N_ROWS = None
PROFILE = False
TASK = "bugginess"

ISSUES_FILE = "data/train/bug_sample_issues.csv"
CHANGES_FILE = "data/train/bug_sample_files.csv"
COMMITS_FILE = "data/train/bug_sample.csv"

TEST_SETS = ["herzig", "berger", "1151-commits"]

LABEL_DATASET_DEBUG = True
LABELED_DATASET_OUTPUT_PATH = "labeled_with_model2.csv"

LABEL_CATEGORIES = ["CommitLabel.NonBugFix", "CommitLabel.BugFix"]
