BOHR (Big Old Heuristic Repository)
----------------------------------

BOHR is a repository of heuristics for categorization of software engineering artifacts, such as commits and bug reports. Categorization of the artifacts is often required to create labeled datasets to train machine learning models on. Since manual labeling is expensive, researchers come up with imprecise heuristics that can assign labels to artifacts. The goal of BOHR is to let researchers contribute a large number of heuristics which are "smartly" combined by `snorkel <https://www.snorkel.org/>`_, the state-of-the art `weak supervision <http://ai.stanford.edu/blog/weak-supervision/>`_ tool.

BOHR is a wrapper around snorkel which:

* Simplifies the process of adding new heuristics and evaluating their effectiveness;
* Labels the datasets registered with BOHR and automatically updates the labels once heuristics are added;
* Keeps track of heursitics used for each version of generated dataset, and in general makes sure the datasets are reproducible and easily accessable by using `DVC <https://dvc.org>`_.


.. contents:: **Contents**
  :backlinks: none

Getting started with BOHR
===========================================

Python >= 3.8 is required, use of virtual environment is strongly recommended.

#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Install BOHR framework library: ``chmod +x bin/setup-bohr.sh && bin/setup-bohr.sh``. This will install `bohr-framework <https://github.com/giganticode/bohr-framework>`_, dependencies and tools to run heursistics.

Downloading datasets and models
===============================

#. Run ``bohr repro``

Bohr extensively uses `DVC (Data Version Control) <https://dvc.org/>`_ to ensure of the datasets and models.

Contributing to BOHR:
=====================


1. Heuristics:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Heuristics can be found in ``.py`` files in the ``bohr/heuristics`` directory, and are marked with @Heuristic decorator. Example:

.. code-block:: python
 
    @Heuristic(Commit)
    def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
        if len(commit.files) > 6:
            return CommitLabel.NonBugFix
        else:
            return None
            
Important things to note:

#. Any function becomes a heuristic once it is marked with ``@Heuristic`` decorator
#. Artifact type is passed to heuristic decorator as a parameter; method accepts an object of artifact type
#. Method name can be arbitrary as long it is unique and descriptive
#. Method should return ``label`` if a datapoint should be labeled with ``label``, ``None`` if the labeling function should abstain on the datapoint

Please refer to the `documentation <https://giganticode.github.io/bohr/Heuristics.html>`_ for more information on heuristics and special heuristic types.        

2. New tasks:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tasks are defined in the `bohr.json` file. Below you can see an example of "bugginess" task.

.. code-block:: json

   "bugginess": {
      "top_artifact": "bohr.artifacts.commit.Commit",
      "label_categories": [
        "CommitLabel.NonBugFix",
        "CommitLabel.BugFix"
      ],
      "test_datasets": [
        "datasets.1151-commits",
        "datasets.berger",
        "datasets.herzig"
      ],
      "train_datasets": [
        "datasets.bugginess-train"
      ],
      "label_column_name": "bug"
    }



The name of the task is the key in the dictionary. The value is an object with the following fields:

#. **Top artifact** - the artifact to be catigorized. In the case of "bugginess" task, commits are classified, therefore the top artifact is ``bohr.artifacts.commit.Commit``;
#. **Label categories** - categories artifact to be classified as, for "bugginess" taks these are *CommitLabel.BugFix* and *CommitLabel.NonBugFix*. Values has to be taken from the ``labels.py`` file. See section `3. Labels:`_ on more information about labels in bohr and how to extend the label hierarchy.
#. **Training sets** - datasets used to train a label model;
#. **Test sets** - datasets to calculate metrics on.

3. Labels:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Labels that are used to label artifacts in BOHR are pre-defined and can be reused across multiple tasks. E.g., ``Commit.Refactoring`` label can be used in heuristics for the tasks of detecting refactoring, but also in the task of detecting bug-fixing commits. Moreover, labels are organized in a hierarchy, e.g. ``Commit.FileRenaming`` can be a child of ``Commit.Refactoring``. Formally speaking, there is a binary relation IS-A defined on the set of labels, which defines their partial order, e.g. ``IS-A(Commit.FileRenaming, Commit.Refactoring)``           

Labels are defined in text files in the ``bohr/labels`` dir. Each row has a format: <parent>: <list of children>. Running ``bohr parse-labels`` will generate `labels.py` file in the root of the repository. Thus to extend the hierarchy of labels it's sufficient to make a change to a text file. The `label.py` will be regenerated, once the PR is received.

4. Datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A datasets are added by creating a dataset file in ``datasets`` folder. The name of the file will correspond to the name of the dataset. e.g.:

*datasets/1151-commits.py*:

.. code-block:: python

  from pathlib import Path

  from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
  from bohr.templates.datamappers.commit import CommitMapper

  dataset_loader = CsvDatasetLoader(
      path_to_file="data/bugginess/test/1151-commits.csv",
      mapper=CommitMapper(Path(__file__).parent.parent),
      test_set=True,
  )

  __all__ = [dataset_loader]
  
In this file, an instance of ``CsvDatasetLoader`` object is created, which is added to the __all__ list (important!)

Dataloader can be an instance of custom ``DatasetLoader`` implementing the following interface:

.. code-block:: python

  @dataclass
  class DatasetLoader(ABC):
    test_set: bool
    mapper: ArtifactMapper
    
    @abstractmethod
    def load(self, project_root: Path) -> DataFrame:
        pass

    @abstractmethod
    def get_paths(self, project_root: Path) -> List[Path]:
        pass
        
*ArtifactMapper* object that has to be passed to the ``DatasetLoader`` defines how each datapoint is mapped to an artifact object and has to implement the following interface:

.. code-block:: python

  class ArtifactMapper(BaseMapper, ABC):
      @abstractmethod
      def __call__(self, x: DataPoint) -> Artifact:
          pass
          
      @abstractmethod
      def get_artifact(self) -> Type[Artifact]:
          pass
          
``bohr.templates.datamappers`` in the bohr-framework lib provide some predefined mappers.

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


