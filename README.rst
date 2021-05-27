BOHR (Big Old Heuristic Repository)
----------------------------------

|GitHub license| |Maintainability| |GitHub make-a-pull-requests|

BOHR is a **repository of heuristics** for categorization of software engineering artifacts, e.g. commits, bug reports, etc. 

Categorization of artifacts is often required to create ground-truth datasets to train machine learning models on. For example, to train a model that classifies commits as "feature", "bugfix", or "refactoring", one needs to have a dataset of commits with these labels assigned. 

Since creating a large dataset manually is expensive, the alternative is to come up with "heuristics", short programs that can assign noisy labels to artifacts automatically. Implementing **a large number of such heuristics** and **combining their outputs** "smartly" is the idea behind `snorkel <https://www.snorkel.org/>`_, the state-of-the-art `weak supervision <http://ai.stanford.edu/blog/weak-supervision/>`_ tool.

BOHR is a wrapper around snorkel which:

* **Simplifies** the process of **adding new heuristics** and **evaluating their effectiveness**;
* **Labels the datasets** registered with BOHR and **automatically updates the labels** once heuristics are added;
* Keeps track of heursitics used for each version of generated datasets and models, and, in general, makes sure they are **reproducible** and **easily accessable** by using `DVC <https://dvc.org>`_.


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

#. A heuristics is marked with the ``Heuristic`` decorator, and the artifact type to which it is applied is passed to it as a parameter; 
#. The artifact instance is exposed to the heuristic as a function parameter; the properties of the artifact object can be used to implement the logic;
#. For the label to be assigned to the artifact, it has to be returned from the function; the heuristic must assign one of the labels defined in the BOHR label hierarchy or ``None`` if it abstains on the data point.

BOHR usage scenarios
===================================

1. Only using existing heuristics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Heuristics already implemented in BOHR are used to train label models, which are continuosly improved as more heuristics are added. The label models are used then to label the datasets that been added to BOHR. These datasets can be easily accesed and used as tehy are. Moreover, you can use the label models to label your own datasets.
 
2. Implementing new heuristics for existing tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to work on already defined tasks, you can add more heuristics to improve the label model and the datasets further. Once new heuristics are implemented, they can be submitted as a pull request to BOHR, which will automatically re-run the pipiline - re-train the label model, re-label the datasets, and calculate new metrics. The pull request will be accepted if the metrics are improved.


3. Implementing heuristics for new tasks and artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BOHR is designed to be extensible. You can esily define new artifact classes and tasks, and start implementing heuristics for those tasks. Note that some heuristics already added for other tasks might be reused for a new task. Please refer to the documentation for more details.

Overview of BOHR abstractions
================================

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



Contribute to the framework
=============================

To contribute to the framework, please refer to the documentation in the  the `bohr-framework <https://github.com/giganticode/bohr-framework>`_ repo.


Pre-prints and publications
=============================

.. code-block::

  @misc{babii2021mining,
        title={Mining Software Repositories with a Collaborative Heuristic Repository}, 
        author={Hlib Babii and Julian Aron Prenner and Laurin Stricker and Anjan Karmakar and Andrea Janes and Romain Robbes},
        year={2021},
        eprint={2103.01722},
        archivePrefix={arXiv},
        primaryClass={cs.SE}
  }


.. |GitHub license| image:: https://img.shields.io/github/license/Naereen/StrapDown.js.svg
   :target: https://github.com/Naereen/StrapDown.js/blob/master/LICENSE
   
.. |GitHub make-a-pull-requests| image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
   :target: http://makeapullrequest.com
   
.. |Maintainability| image:: https://codeclimate.com/github/giganticode/bohr/badges/gpa.svg
   :target: https://codeclimate.com/github/giganticode/bohr
   :alt: Code Climate

