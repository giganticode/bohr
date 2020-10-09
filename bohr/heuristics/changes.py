from bohr.snorkel_utils import Commit, Label, commit_lf


@commit_lf()
def no_files_have_modified_status(commit: Commit) -> Label:
    for file in commit.files:
        if file.status == 'modified': return Label.ABSTAIN
        if file.status == 'added': return Label.ABSTAIN
    return Label.BUGLESS