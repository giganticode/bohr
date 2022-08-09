BOHR (Big Old Heuristic Repository)
----------------------------------

|GitHub license| |Maintainability| |GitHub make-a-pull-requests|

BOHR is a **repository of heuristics** for preparation (labeling, grouping, linking, filtering) of software engineering artifacts, e.g. commits, bug reports, code snippets, etc. Preparation of these artifacts is often required by researchers in the field of Software Engineering (SE) and Mining Software Repositories (MSR) to convert artifacts mined from software repositories such as GitHub, StackOverflow into datasets that can be used for empirical experiments and for training machine learning models. An example could be classifying commits mined from GitHub into bug-fixing and others in order to create a training dataset to train a machine-learning model on. 

Preparing each artifact manually is expensive and does not scale well. Therefore BOHR offers an approach to define heuristics (short functions) to do the job automatically. Even though using heuristics is usually less accurate than letting experts analyse each artifacts, we claim that using a large number of diverse heuristics and combining them "smartly" can significantly reduce the noise compared to for example using one heuistic. The way heuristics are combined depends on the type of the task, but one of the most common way is to use the algorithm used by the `snorkel <https://www.snorkel.org/>`_, the state-of-the-art `weak supervision <http://ai.stanford.edu/blog/weak-supervision/>`_ tool.   

.. contents:: **Contents**
  :backlinks: none


Examples of tasks and heuristics
=======================================

Commit classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One example is classifying commits mined from GitHub into "bugfix" and "non-bugfix", in order to create a training dataset to train a machine-learning model on. 

 .. code-block:: python
 
  # ... other imports
  
  from bohrapi.core import Heuristic
  from bohrlabels.core import OneOrManyLabels

  from bohrapi.artifacts import Commit
  from bohrlabels.labels import CommitLabel


  @Heuristic(Commit)
  def bugless_if_many_files_changes(commit: Commit) -> OneOrManyLabels:
      if len(commit.commit_files) > 15:
          return CommitLabel.NonBugFix
      else:
          return None

Grouping online identities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Important things to note:

#. A heuristics is marked with the ``Heuristic`` decorator, and the artifact type to which it is applied is passed to it as a parameter; 
#. The artifact instance is exposed to the heuristic as a function parameter; the properties of the artifact object can be used to implement the logic;
#. The label assigned to the artifact by the heuristic is the result of the execution on the passed artifact object; the heuristic must assign one of the labels defined in the BOHR label hierarchy or ``None`` if it abstains on the data point.




TBD: Insert somewhere later?

* **Simplifies** the process of **adding new heuristics** and **evaluating their effectiveness**;
* **Labels the datasets** registered with BOHR and **automatically updates the labels** once heuristics are added;
* Keeps track of heursitics used for each version of generated datasets and models, and, in general, makes sure they are **reproducible** and **easily accessable** by using `DVC <https://dvc.org>`_.

 

Main Concepts (maybe this is not needed in README, rather in the docs)
====================================

BOHR is a repository of *heuristics*, hence, a heuristic is a primary concept in BOHR. Sub-program (python function) that accepts an artifact or multiple artifacts of the same or different types. 

Artifact is BOHR's abstraction that represents a software engineering artifact - a product of SE activities, e,g. code, commit, software project, software repository, issue report. *Dataset* is a collection of artifacts of the same type. 

*Task* is an abstraction that describes the problem that a researcher is working on in terms of BOHR. The input and the output of the tasks are datasets. Task types are labeling, grouping, linking, filtering. The task is defined by specifying artifact type(s) heuristics are applied to, possible outputs of heuristics, strategy how heuristics aree combined, test datasets and metrics to use to evaluate the effectiveness of heuristics.

*Experiment* is an attempt to solve a task using a specific set of heuristics (and training data if needed).


BOHR workflow
===================================


1a. For the given task, pull existing heuristics developed by community
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bohr clone https://github.com/giganticode/bohr-workdir-bugginess``

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

TODO: add links to other repos

Pre-prints and publications
=============================

If you use BOHR in your research, please cite us:

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

