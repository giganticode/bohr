BOHR (Big Old Heuristic Repository)
----------------------------------

|GitHub license| |Maintainability| |GitHub make-a-pull-requests|

BOHR is a **repository of heuristics** for preparation (filtering, labeling, grouping, filtering) of software engineering (SE) artifacts, e.g. commits, bug reports, code snippets, etc. SE artifact preparation is often required by researchers in the field of Software Engineering and Mining Software Repositories (MSR) to convert artifacts mined from software repositories into datasets that can be used to conduct empirical experiments and to train machine learning models. 

Preparing each artifact manually is expensive and does not scale well. Therefore BOHR offers an approach to define heuristics to do the job automatically. Even though heuristic outputs can be noisy by their definition, using a large number of them and "smartly" combining them compensates for the quality of outputs. 



TBD:


Examples
=====================

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
  from bohrlabels.core import OneOrManyLabels

  from bohrapi.artifacts import Commit
  from bohrlabels.labels import CommitLabel


  @Heuristic(Commit)
  def bugless_if_many_files_changes(commit: Commit) -> OneOrManyLabels:
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

