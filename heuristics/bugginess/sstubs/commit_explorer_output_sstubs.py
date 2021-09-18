@Heuristic(Commit)
def commit_explorer_output_sstubs(commit: Commit) -> Optional[Labels]:
    try:
        if commit.commit_explorer_data is None:
            return None

        data = commit.commit_explorer_data
        if "mine_sstubs/head" in data and data["mine_sstubs/head"]:
            print("Contains bug")
            return l.CommitLabel.BugFix
    except (CommitExplorerClientException, CommitNotFoundException) as ex:
        return None
