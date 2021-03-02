Special heuristic types:
~~~~~~~~~~~~~~~~~~~~~~~~

There are some common types of heuristics that are abstacted away, among which are *keyword heuristics* and *tool heuristics*.

Keyword heuristics:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Example.

.. code-block:: python

    @KeywordHeuristics(Commit, "bug", name_pattern="bug_message_keyword_%1")
    def bug_keywords_lookup_in_message(commit: Commit, keywords: NgramSet) -> Optional[Labels]:
        if commit.message.match_ngrams(keywords):
            return CommitLabel.BugFix
        return None
        
Tool heuristics:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Example.

.. code-block:: python

    @ToolOutputHeuristic(Commit, tool=RefactoringMiner)
    def refactorings_detected(commit: Commit, refactoring_miner: RefactoringMiner) -> Optional[Labels]:
        refactoring_miner_output = refactoring_miner.run(commit)
        if len(refactoring_miner_output.commits[0].refactorings) > 0:
            return CommitLabel.Refactoring
        return None
