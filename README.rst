BOHR (Big Old Heuristic Repository)
----------------------------------

BOHR is a **repository of heuristics** for categorization of software engineering artifacts, e.g. commits, bug reports, etc. 

Categorization of artifacts is often required to create ground-truth datasets to train machine learning models on. For example, to train a model that classifies commits as "feature", "bugfix", or "refactoring", one needs to have a dataset of commits with these labels assigned. 

Since creating a large dataset manually is expensive, the alternative is to come up with "heuristics", short programs that can assign noisy labels to artifacts automatically. Implementing **a large number of such heuristics** and **combining their outputs** "smartly" is the idea behind `snorkel <https://www.snorkel.org/>`_, the state-of-the-art `weak supervision <http://ai.stanford.edu/blog/weak-supervision/>`_ tool.

BOHR is a wrapper around snorkel which:

* **Simplifies** the process of **adding new heuristics** and **evaluating their effectiveness**;
* Labels the datasets registered with BOHR and **automatically updates the labels** once heuristics are added;
* Keeps track of heursitics used for each version of generated datasets and model, and, in general, makes sure they are **reproducible** and **easily accessable** by using `DVC <https://dvc.org>`_.


.. contents:: **Contents**
  :backlinks: none
  
How do heuristics look like?
===================================
  
 .. code-block:: python
 
    # other imports
    ...
    from bohr.core import Heuristic
    from bohr.collection.artifacts import Commit
    from bohr.labels import CommitLabel
 
    @Heuristic(Commit)
    def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
        if len(commit.files) > 6:
            return CommitLabel.NonBugFix
        else:
            return None
            
Important things to note:

#. Heuristics are marked with ``Heuristic`` decorator and the artifact type is passed to it as a parameter; 
#. An object of the artifact type is exposed as a parameter to the function, and its properties can be used to implement the logic;
#. An artifact is assigned a label returned from the function; the heuristic must assign one of the labels defined in the BOHR label hierarchy or ``None`` if it abstains on this data point.

BOHR usage scenarios
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

Heuristics should be defined in ``.py`` files in the ``heuristics`` directory. In order to train a new label model and to re-label the datasets with improved labels after adding new heuristics, run ``bohr repro``.

Please refer to the `documentation <https://giganticode.github.io/bohr/Heuristics.html>`_ for more information on heuristics and special heuristic types.        


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

Quick Start
============

Installation
~~~~~~~~~~~~~

Python >= 3.8 is required, use of virtual environment is strongly recommended.

#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Install BOHR framework library: ``bin/setup-bohr.sh``. This will install `bohr-framework <https://github.com/giganticode/bohr-framework>`_, dependencies and tools to run heursistics.

Important commands
~~~~~~~~~~~~~~~~~~~

+-----------------------------------+-------------------------------------------------------------------+
|                                   | Command                                                           |
+===================================+===================================================================+
| Pull existing labeled dataset     | | ``$ bohr pull bugginess 200k-commits``                          |
+-----------------------------------+-------------------------------------------------------------------+
| Label your dataset                | | ``$ bohr dataset add ~/new_commit_dataset.csv -t commit``       |
|                                   | | ``$ bohr task add-dataset bugginess new_commit_dataset --repro``|      
+-----------------------------------+-------------------------------------------------------------------+
| Add heuristic(s), re-train        | | ``$ vi heuristics/commit_files.py``                             |
| label model, and update labels    | | ``$ bohr repro bugginess``                                      |
+-----------------------------------+-------------------------------------------------------------------+
| Add a new task                    | | ``$ bohr task add tangled-commits \``                           |
|                                   | | ``...    -l TangledCommit.NonTangled,TangledCommit.Tangled \``  |
|                                   | | ``...    --repro``                                              |
|                                   | |                                                                 |
+-----------------------------------+-------------------------------------------------------------------+



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


