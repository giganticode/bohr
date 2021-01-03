BOHR
----------------------------------
Big Old Heuristic Repository

Getting started
===========================================

Install Anaconda/Miniconda
~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Install conda_ [Skip this step if you already have conda installed]
#. Create a virtual environment ``conda create --name <YOUR ENV NAME> python==3.8.0`` 
#. Activate virtual environment ``conda activate <YOUR ENV NAME>`` 

Get started with BOHR
~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Run `pip install --upgrade pip setuptools wheel` (Python 3.8 or higher is required)
#. Run ``pip install -r requirements.txt`` 

Running the code and reproducing the models
===========================================

Using DVC (Data Version Control) - preferred
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install dvc_ for your OS

#. Install p7zip_ for your OS

#. Setting up datasource. Ironspeed users should create a file ``.dvc/config.local``. Dvc will check this file to know where datasets should be fetched from on the next step. It contains sensitive data, must not be committed, and is gitignored by default. The contents of the file should be the following::

    [core]
        remote = ironspeed
    ['remote "ironspeed"']
        url = ssh://10.10.20.160/home/hbabii/.dvcstorage/bohr
        user = <username>
        password = <password>

#. Run ``dvc pull -r ironspeed data/test downloaded-data/b_b.7z``

#. Run ``dvc repro``

.. _dvc: https://dvc.org/doc/install
.. _p7zip: https://www.7-zip.org
.. _conda: https://docs.anaconda.com/anaconda/install/

Without DVC
~~~~~~~~~~~
TBA



EDIT TEXT BELOW WITH UPDATED STEPS >>>

Contribute to the project by adding your first heuristic:
===========================================================

#. Define a function inside the ``bohr/heuristics/templates.py`` file and label it with @labeling_function() decorator. This heuristic can be reused later for different tasks.

#. To use the newly created function to label commits for a specific task, add it to the ``heuristics`` list defined in ``bohr/heuristics/<task>/<label>.py`` (e.g., for the task of classification of bugfix commit for a bugfix commit, the file is ``bohr/heuristics/bugs/bugs.py``)

#. Run ``dvc repro`` to recalculate the metrics or (if not using DVC) rerun the scripts in ``bohr/pipeline`` package manually

#. Commit and push the changes together with the changed metric files.

See this commit_ as an example of how a heuristic can be added.

.. _commit : https://github.com/giganticode/bohr/commit/6928dfd750d304ca4610dbba4216f6e94375e4a7

Credits
=======

This project is based on the work of `@lalenzos <https://github.com/lalenzos>`_ and partially uses his code.
