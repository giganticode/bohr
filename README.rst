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
 
  # ... other imports
  
  from bohrapi.core import Heuristic
  from bohrlabels.core import Labels

  from bohrapi.artifacts import Commit
  from bohrlabels.labels import CommitLabel


  @Heuristic(Commit)
  def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
      if len(commit.commit_files) > 15:
          return CommitLabel.NonBugFix
      else:
          return None
            
Important things to note:

#. A heuristics is marked with the ``Heuristic`` decorator, and the artifact type to which it is applied is passed to it as a parameter; 
#. The artifact instance is exposed to the heuristic as a function parameter; the properties of the artifact object can be used to implement the logic;
#. The label assigned to the artifact by the heuristic is the result of the execution on the passed artifact object; the heuristic must assign one of the labels defined in the BOHR label hierarchy or ``None`` if it abstains on the data point.

Main Concepts
====================================

Apart from heuristics, main concepts of BOHR are **artifacts**, **datasets**, **labels**, **label assigners**, and **tasks**.

**Artifact** is a central concept. It is a result of software engineering activity, e.g., code, commit, software project, software repository, issue report. 

A collection of artifacts of the same type forms a **dataset**, which is often produced by MSR activities. The central use-case of BOHR is to assign labels to a dataset according to the given **task**. The purpose of assigning labels is to prepare datasets to be used in empirical studies or for training machine learning models. 

**Labels** can be attached to artifacts and generally speaking can contain arbitrary information. Based on labels artifacts can be filtered or categorized.

Labels to artifacts are assigned by **assigners**. There are **single-artifact** and **bulk** assigners. Single-artifact assigners assign labels directly to specific artifacts. These are normally human assigners that assign label to artifacts one by one (possibly as part of actively learning approach to be implement as part of BOHR). Bulk assigners are programs that infer the label to be assigned from the given input artifact. Examples of bulk assigners are heuristics themselves, their combinations (majority vote and label models), and deep learning models. 

W.r.t. the presence of labels for the given task, datasets can be classified as **labeled** or **unlabeled**. Labeled datasets can be labeled with single-artifact assigners or with bulk-assigners. Even though, we consider datasets labeled by single-artifact assigners to be ground truth datasets, the border between ground-truth labels and not are blurry, see agree-to-disagree section.

By working on a **task**, researchers aim to assign labels to datasets according to the rules defined by the task. E.g. there can be a task according to which an artifact can be assigned "bug-fixing" xor "non-bug-fixing" labels. The approach of assigning labels (mostly by using a trained bulk-assinger) is evaluated on a stand-alone test set(s), which has labels assigned according to strictly-defined rules.  


BOHR workflow
===================================

1. Get the list of pre-defined tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bohr tasks``

2. For the given task, pull existing heuristics developed by community
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bohr clone bugginess ~/bugginess-work-dir``

This will clone the so called BOHR working directory that corresponds to the <task> to <path>

3 Check whether the existing labeled datasets are suitable for your purposes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every task comes with a trained classifier and a default dataset labeled by this classifier. Check whether the default datasets suits your purposes.

``cd bugginess-work-dir && bohr pull default``

The path where dataset is load will be displayed.

4. Label your own dataset with the default classifier.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``$ bohr dataset add ~/new_commit_dataset.csv``
``$ bohr task add-dataset bugginess new_commit_dataset --repro``

5. Develop a new heuristic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``$ vi heuristics/commit_files.py``


6. Debug and tune the heuristic by checking its coverage and accuracy on a stand-alone test-set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``$ bohr repro``

7. Submit a pull request with the new heuristic to remote BOHR repository 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``$ bohr upload``


Label model is trained and metrics are calculated on stand-alone test set as a part of a CI-pipeline. If metrics has been improved, the new heuristic is added to BOHR, and is available for other researchers.

8. Add a new task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``$ bohr task add tangled-commits \``
``...    -l TangledCommit.NonTangled,TangledCommit.Tangled \``
``...    --repro``



Installation
==============

Python >= 3.8 is required, use of virtual environment is strongly recommended.

#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Install BOHR framework library: ``bin/setup-bohr.sh``. This will install `bohr-framework <https://github.com/giganticode/bohr-framework>`_, dependencies and tools to run heursistics.


Contribute to the framework
=============================

To contribute to the BOHR-framework, which is used to manage the BOHR repo, please refer to the `bohr-framework repo <https://github.com/giganticode/bohr-framework>`_.


Pre-prints and publications
=============================

.. code-block::

    @inproceedings{babii2021mining,
      title={Mining Software Repositories with a Collaborative Heuristic Repository},
      author={Babii, Hlib and Prenner, Julian Aron and Stricker, Laurin and Karmakar, Anjan and Janes, Andrea and Robbes, Romain},
      booktitle={2021 IEEE/ACM 43rd International Conference on Software Engineering: New Ideas and Emerging Results (ICSE-NIER)},
      pages={106--110},
      year={2021},
      organization={IEEE}
    }


.. |GitHub license| image:: https://img.shields.io/github/license/giganticode/bohr.svg
   :target: https://github.com/giganticode/bohr/blob/master/LICENSE
   
.. |GitHub make-a-pull-requests| image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
   :target: http://makeapullrequest.com
   
.. |Maintainability| image:: https://codeclimate.com/github/giganticode/bohr/badges/gpa.svg
   :target: https://codeclimate.com/github/giganticode/bohr
   :alt: Code Climate

