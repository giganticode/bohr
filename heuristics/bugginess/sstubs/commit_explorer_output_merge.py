@Heuristic(Commit)
def commit_explorer_output_merge(commit: Commit) -> Optional[Labels]:
    try:
        if commit.commit_explorer_data is None:
            return None

        if (
            "special_commit_finder/0_1" in commit.commit_explorer_data
            and commit.commit_explorer_data["special_commit_finder/0_1"]["merge"]
        ):
            return l.CommitLabel.Merge
    except (CommitExplorerClientException, CommitNotFoundException) as ex:
        return None
