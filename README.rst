BOHR (Big Old Heuristic Repository)
----------------------------------

BOHR is a repository of heuristics for categorization of software engineering artifacts, such as commits and bug reports. Categorization of the artifacts is often required to create labeled datasets to train machine learning models on. Since manual labeling is expensive, researchers come up with imprecise heuristics that can assign labels to artifacts. The goal of BOHR is to let researchers contribute a large number of heuristics which are "smartly" combined by `snorkel <https://www.snorkel.org/>`_, the state-of-the art `weak supervision <http://ai.stanford.edu/blog/weak-supervision/>`_ tool.

BOHR is a wrapper around snorkel which:

* Simplifies the process of adding new heuristics and evaluating their effectiveness;
* Labels the datasets registered with BOHR and automatically updates the labels once heuristics are added;
* Keeps track of heursitics used for each version of generated dataset, and in general makes sure the datasets are reproducible and easily accessable by using `DVC <https://dvc.org>`_.


.. contents:: **Contents**
  :backlinks: none

Installation
===========================================

Python >= 3.8 is required, use of virtual environment is strongly recommended.

#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Install BOHR framework library: ``bin/setup-bohr.sh``. This will install `bohr-framework <https://github.com/giganticode/bohr-framework>`_, dependencies and tools to run heursistics.

Scenarios of using BOHR
===================================

.. raw:: html

    <img src="doc/reuse_levels.gif" width="600px">

1. Using labeled datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``bohr pull`` command. For example, to download ``200k-commits`` labeled by the ``bugginess`` task, run:

``bohr pull bugginess 200k-commits``

Bohr extensively uses `DVC (Data Version Control) <https://dvc.org/>`_ to ensure the integrity and reproducibility of the datasets and models.

2. Label your own dataset with an existing model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

3. Adding heuristics for existing task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Heuristics should be defined in ``.py`` files in the ``heuristics`` directory as methods marked with @Heuristic decorator. Below you can see a heuristic which marks a commit as non-bug-fixing if it has contains more than 6 modified files: 

.. code-block:: python
 
    @Heuristic(Commit)
    def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
        if len(commit.files) > 6:
            return CommitLabel.NonBugFix
        else:
            return None


Important things to note:

#. Artifact type is passed to heuristic decorator as a parameter; an object of the same type is exposed as a parameter to the function;
#. Method name can be arbitrary as long it is unique and descriptive;
#. Method should return the label which which the current commit is to be labeled, ``None`` if the labeling function should abstain on the datapoint. The label can be one of the objects defined in ``label.py``. See ... for more details on *label hierarchy*.

Please refer to the `documentation <https://giganticode.github.io/bohr/Heuristics.html>`_ for more information on heuristics and special heuristic types.        

In order to train a new label model and to relabel the datasets with improved labels after adding new heuristics, run ``bohr repro``.

4. Adding a new task
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a new taks, run ``bohr task add`` command. For example, for a tasks of classifying commit as tangled or not:

.. code-block::

  bohr task add tangled-commits \
      -d "Task to classify commits into tangled and non-tangled"          # description
      -t commit                                                           # artifact to be classified
      -l TangledCommit.NonTangled,TangledCommit.Tangled                   # comma-separated label list for the classifier to choose from
      -c tangled                                                          # column with ground-truth labels
      --force                                                             # rewrite if the task with the same name already exists
      --use-all-datasets                                                  # use all the datasets found in BOHR that contain the artifact being classified
      --repro                                                             # apply right away compatible heuristics, generate a label model and label the datasets


Overview of BOHR abstractions
====================================

.. raw:: html

    <img src="doc/bohr_abstractions.png" width="600px">




The name of the task is the key in the dictionary. The value is an object with the following fields:

#. **Top artifact** - the artifact to be catigorized. In the case of "bugginess" task, commits are classified, therefore the top artifact is ``bohr.artifacts.commit.Commit``;
#. **Label categories** - categories artifact to be classified as, for "bugginess" taks these are *CommitLabel.BugFix* and *CommitLabel.NonBugFix*. Values has to be taken from the ``labels.py`` file. See section `3. Labels:`_ on more information about labels in bohr and how to extend the label hierarchy.
#. **Training sets** - datasets used to train a label model;
#. **Test sets** - datasets to calculate metrics on.

3. Labels:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Labels that are used to label artifacts in BOHR are pre-defined and can be reused across multiple tasks. E.g., ``Commit.Refactoring`` label can be used in heuristics for the tasks of detecting refactoring, but also in the task of detecting bug-fixing commits. Moreover, labels are organized in a hierarchy, e.g. ``Commit.FileRenaming`` can be a child of ``Commit.Refactoring``. Formally speaking, there is a binary relation IS-A defined on the set of labels, which defines their partial order, e.g. ``IS-A(Commit.FileRenaming, Commit.Refactoring)``           

Labels are defined in text files in the ``bohr/labels`` dir. Each row has a format: <parent>: <list of children>. Running ``bohr parse-labels`` will generate `labels.py` file in the root of the repository. Thus to extend the hierarchy of labels it's sufficient to make a change to a text file. The `label.py` will be regenerated, once the PR is received.


5 Artifact definitions
~~~~~~~~~~~~~~~~~~~~~~~~
``bohr.templates.artifacts`` also defines some pre-defined artifacts


Contribute to the framework:
=============================

To contribute to the framework, please refer to the documentation in the  the `bohr-framework <https://github.com/giganticode/bohr-framework>`_ repo.


Pre-prints and publications
===========================================

.. code-block::

  @misc{babii2021mining,
        title={Mining Software Repositories with a Collaborative Heuristic Repository}, 
        author={Hlib Babii and Julian Aron Prenner and Laurin Stricker and Anjan Karmakar and Andrea Janes and Romain Robbes},
        year={2021},
        eprint={2103.01722},
        archivePrefix={arXiv},
        primaryClass={cs.SE}
  }


