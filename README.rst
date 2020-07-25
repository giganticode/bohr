BOHR
----------------------------------
Big Old Heuristic Repository

Getting started
===========================================

#. Run ``git clone https://github.com/giganticode/bohr && cd bohr``
#. Create a virtual environment and run ``pip install -r requirements.txt`` (Python 3.7 or higher is required)

Running the code and reproducing the models
===========================================

Using DVC (Data Version Control) - preferred
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Install dvc_

#. Setting up datasource. Ironspeed users should create a file ``.dvc/config.local``. Dvc will check this file to know where datasets should be fetched from on the next step. It contains sensitive data, must not be committed, and is gitignored by default. The contents of the file should be the following::

    [core]
        remote = ironspeed
    ['remote "ironspeed"']
        url = ssh://10.199.39.232/home/<username>/.dvcstorage
        password = <username>
        user = <password>

#. Run ``dvc pull data/combination/Test_Dataset.csv data/combination/Training_Dataset.csv``
#. Run ``dvc repro``

.. _dvc: https://dvc.org/doc/install

Without DVC
~~~~~~~~~~~
TBA

Credits
=======

This project is based on the work of `@lalenzos <https://github.com/lalenzos>`_ and partially uses his code.
