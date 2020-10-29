from bohr.snorkel_utils import Commit, Label, commit_lf


@commit_lf()
def no_files_have_modified_status(commit: Commit) -> Label:
    for file in commit.files:
        if file.status == 'modified': return Label.ABSTAIN
    return Label.BUGLESS


@commit_lf()
def bug_if_only_changed_lines_in_one_file(commit: Commit) -> Label:
    if len(commit.files) == 1 and commit.files[0].status == 'modified' \
            and commit.files[0].changes and commit.files[0].no_added_lines() and commit.files[0].no_removed_lines():
        return Label.BUG
    return Label.ABSTAIN


@commit_lf()
def bugless_if_many_files_changes(commit: Commit) -> Label:
    if len(commit.files) > 6:
        return Label.BUGLESS
    else:
        return Label.ABSTAIN