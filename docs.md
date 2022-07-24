# BOHR Overview

BOHR, apart from being a storage of heuristics, is also an infrastructure and a set of tools for their development, debugging, and usage for solving problems researchers in the field of MSR and SE encounter. 

## BOHR API 

#### Overview

API (python library) to define *datasets*, *tasks*, and *experiments*, and to develop *heuristics* to be applied to *artifacts*.

#### Main Concepts

##### Heuristic

BOHR is a repository of *heuristics*, hence, a heuristic is a primary concept in BOHR. Sub-program (python function) that accepts an artifact or multiple artifacts of the same or different types. Artifact is BOHR's abstraction that represents a software engineering artifact - a product of SE activities, e,g. code, commit, software project, software repository, issue report.

```python
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
```



##### Dataset

Collection of artifacts of the same type (*See Artifact Explorer*)

##### Task

An abstraction that describes the problem that a researcher is working on in terms of BOHR. The input and the output of the tasks are datasets. Task types are 

- labeling, 
- grouping, 
- linking, 
- filtering

To define a task, the BOHR user needs to specify:

- Artifact type(s) heuristics are applied to 

- - Single artifact for labeling and filtering, 
  - pairs of artifacts of the same type for grouping, 
  - pairs of artifacts (most likely of different types) for linking, e.g. Commit and Issue

- Possible outputs of heuristics; 

- - Label for labeling, 
  - True/False for filtering; 
  - probabilistic True/False for grouping and linking

- Heuristic combination strategy (model) 

- - trivial strategy (using only one heuristic), 
  - applying and filtering one by one, 
  - majority vote model, 
  - weighted vote model (snorkel) - for labeling 
  - weighted vote model + clustering using output probabilities as similarity indices - for grouping.

- Metrics;

- Test dataset;

##### Experiment

Attempt to solve a task using a specific set of heuristics and a training set. To define an experiment, the user specifies:

- the target task
- heuristic classifier - heuristics to be used to tackle the task
- train dataset (if required)

The user defines a BOHR configuration to specify which heuristics and datasets should be used to solve a task within an experiment. Configuration is described with code and can look like the code below.



```python
from bohrapi.artifacts import Commit
from bohrapi.core import Dataset, Experiment, LabelingTask
from bohrlabels.labels import CommitLabel

berger_dataset = Dataset(
  id="manual_labels.berger", 
  heuristic_input_artifact_type=Commit,
  ground_truth_label_func=None,
)
herzig_dataset = Dataset(
  id="manual_labels.herzig", 
  heuristic_input_artifact_type=Commit,
  ground_truth_label_func=lambda c: (CommitLabel.BugFix 
                                     if c.raw_data["manual_labels"]["herzig"]["bug"] == 1 
                                     else CommitLabel.NonBugFix)
)


bugginess_task = LabelingTask(
    name="bugginess", author="hlib", description="bug or not",
    heuristic_input_artifact_type=Commit,
    test_datasets=[herzig_dataset],
    labels=[CommitLabel.NonBugFix, CommitLabel.BugFix],
)

keywords_in_message_exp = Experiment(
    name="keywords_in_message",
    task=bugginess_task,
    train_dataset=berger_dataset,
 heuristic_specifier=f"bugginess/keywords/bug_keywords_lookup_in_message.py:bugginess/keywords/buggless_keywords_lookup_in_message.py@0888f28b0c1619c3c8ea4378887ff2633f065691",
)
```



Source code: https://github.com/giganticode/bohr-api

#### BOHR API and Heuristic development

The role of BOHR-API for heuristic development is twofold. First, it provides a skeleton of heuristics for developers, with which they can ensure the heuristics are found and correctly run by the BOHR engine, e.g. @Heuristic annotation, enforcing the input and output of heuristics, etc. Second BOHR-API allows to access properties of artifacts in an easy and representation- and language-independent way (*See Future direction: working on SE heuristic API (aka BOHR API)*).



## BOHR Runtime (BOHR engine)

Experiments defined in the BOHR configuration can be run by exectuing CLI commands exposed by BOHR engine.

*bohr run    keywords_in_message_exp*

*bohr run --no-cache     keywords_in_message_exp*



Each of these commands executed from the directory with the configuration file (BOHR working directory) will run the following steps: 

- collects heuristics used in the current experiment

- load the datasets used

- apply heuristics to the datasets

- combine the otput of heuristic in a way that is dependent on the chosen strategy

- calculate metrics

- prepare the train and test datasets according to the developed model.

  

The source code of bohr-runtime can be found at https://github.com/giganticode/bohr-runtime



#### Heuristic Debugging 

**! This section to be updated accoring with the new vision of BOHR !**

BOHR engine provides utilities to debug the application and combining of heuristics 

*bohr debug  \<exp-name\> \<dataset-name\>*

![image](https://user-images.githubusercontent.com/2955794/114852200-d95f4000-9de2-11eb-9476-2dd23ac09bc9.png)

*bohr debug  \<exp-name\> \<dataset-name\> \<datapoint-id\>*

![image](https://user-images.githubusercontent.com/2955794/114852453-14fa0a00-9de3-11eb-8d90-858bf625060b.png)



Alternatively, BOHR-UI can be used to perform debugging (*see BOHR-UI*) 



## Architecture of BOHR

BOHR (The repository of heuristics itself) can be accessed at https://github.com/giganticode/bohr  (we will be calling it *the remote BOHR repository*). This is where BOHR-runtime (engine) fetches the heuristics from after reading user's BOHR config. The remote BOHR repo is cloned to the local machine next to the BOHR config. Since the heuristics require the BOHR-API to run them, Bohr-runtime installs the needed version of the BOHR-API. BOHR-Runtime runs the pipeline and generates locally all the intermediate artifacts (results of heuristic runs, trained models, calculated metrics). The directory with the BOHR config, cloned heuristics, intermediate artifacts is called BOHR working directory.

The user can make changes and add new heuristics to the local BOHR repo. Then they can send a pull request with the changes to the remote BOHR repo.The remote BOHR repo has a CI pipeline set up with the BOHR runtime rerunning the whole fetch-apply-train-evaluate pipeline. The changes to heuristics are merged once the pipeline succeeds.

![image-20220704170725884](/Users/hlib/Library/Application Support/typora-user-images/image-20220704170725884.png)

### Sharing tasks and experiments

Apart from sharing heuristics, the entire task and task runs (experiments) can be shared. We find the link Git+DVC useful for sharing tasks and experiments. The BOHR config for the task + metrics can be stored in Git, all large intermediate artifacts can be stored in DVC.

*bohr clone https://github.com/giganticode/bohr-workdir-bugginess* -> pulls from git, pulls from dvc, makes sure everything is up-to-date, otherwise reproduces.

See an example https://github.com/giganticode/bohr-workdir-bugginess



## Artifact Explorer

BOHR provides two ways to work with datasets. First, BOHR allows to add datasets to the working directory and lets the BOHR engine load datasets from there (NOT IMPLEMENTED yet). In this case, if the user decides to share their task and experiments, they would have to share their dataset along with them. The second way, which works especially well for well-known datasets that are used by multiple studies, is to load datasets from Artifact Explorer by specifying a query. When the experiments are made public, only the dataset id or the query needs to be shared (part of the dataset configuration in the BOHR config file). Then the user that wants to reproduce the study will use the dataset's metadata to pull the dataset from Artifact Explorer.

To give as much power to heuristic developers as possible, we want them to be able to access a wide range of information about artifacts. First, these is properties of artifacts extracted when mining them (e.g. files that commit contains). Second, information is extracted from artifacts using specific tools (e.g. refactoring that commit contains detected by the RefactoringMiner tool). The problem with the former is that running tools can be costly and getting it on demand might not be feasible. The solution is to cache the runs of the tools and reuse them between different heuristic runs. Here comes another advantage of loading datasets from Artifact Explorer. Artifact explorer contains rich information about artifacts and contains the outputs of different tools run on them. 

Two important parts of Artifact Explorer are the database + client and the crawler.

#### Database + HTTPServer + Client

Artifact explorer stores information at mongo db: mongodb://read-only-user:123@10.10.20.160:27017 (ironspeed)

A few request examples:

- {"manual_labels.berger": {"$exists": true}}
- {"_id": "30b9871ceef52cd43b830c058a3a3d34c36eb742"}



HTTP client is running at: http://squirrel.inf.unibz.it:8180/art-exp/ (for now accessible only from the university network)

You can try, fir example, accessing the following commit: http://squirrel.inf.unibz.it:8180/art-exp/commit/5959170e460d5cfa11b9f32a84ad91487151df0b





#### Crawler

The crawler continuously adds new artifacts to the database and runs the tools on them, so that as much information as possible were availbale to the researchers. The tool is normally run on the ironspeed server.

One could feed the jobs in the following format to the Artifact Explorer crawler:

```json
{"tools": ["gumtree/3.0.0-beta2"], "projects": ["0x43/DesignPatternsPHP", "AlexMeliq/less.js", "Arcank/nimbus", "AutoMapper/AutoMapper", "Chenkaiang/XVim", "GeertJohan/gorp", "K2InformaticsGmBH/proper", "MerlinDMC/gocode", "MythTV/mythtv", "alibaba/tengine", "clojure/core.logic", "docpad/docpad", "faylang/fay", "lfe/lfe", "magicalpanda/MagicalRecord", "mpeltonen/sbt-idea", "plumatic/plumbing", "sinclairzx81/typescript.api", "yu19930123/ngrok", "apache/httpcomponents-client", "apache/jackrabbit", "apache/lucene-solr", "apache/tomcat", "mozilla/rhino", "JetBrains/intellij-community", "JetBrains/kotlin", "ReactiveX/RxJava", "apache/camel", "apache/hadoop", "apache/hbase", "elastic/elasticsearch", "kiegroup/drools", "orientechnologies/orientdb", "restlet/restlet-framework-java", "spring-projects/spring-framework"]}
```



Source code https://github.com/giganticode/commit-explorer

 

## BOHR-Labels and Label taxonomy

Two core ideas of BOHR for labeling tasks are 1) reusing heuristics developed for more specific tasks for more general tasks  2) Reusing heuristics accross different label definitions.

The source code of can be found at https://github.com/giganticode/bohr-labels



![image-20220708233442302](/Users/hlib/Library/Application Support/typora-user-images/image-20220708233442302.png)

#### Concept of *label* in BOHR.

Labels are used in labeling tasks and heuristics compatible with these task.1) Labeling task heuristics assign BOHR labels to artifacts. 2) When a labeling task is defined, BOHR labels are used to define categories to which artifacts can be categorized.

Labels are organized in a hierarchy in BOHR (see the graph).  To be more precise, we define it as a multi-hierarchy, in which two labels can either be 1) in a relationship "ancestor-descendent" (or "more generic - more specific", e.g. BugFix and MajorBugFix or 2) be mutually exclusive, e,g, NonBugFix and UIBugFix or 3) be not mutually exclusive, e.g. MinorBugFix and UIBugFix. 

A group of labels belongs to the same hierarchy if and only if 



Heuristic can assign multiple labels, each pair of which are from different hierarchies, e.g. ConcurrencyBugFix and MajorBugFix.

 When the task is e.g. MinorBugFix vs MajorBugFix, only the label MajorBugFix label is considered. 

Labels defined in the task have to be mutually exclusive, i.e. have to be from the same hierarchy.



#### Labels implementation



https://stackoverflow.com/questions/70145416/collapsible-subset-of-partially-ordered-set



## Applications

#### Commit classification

https://github.com/giganticode/bohr-workdir-bugginess

#### Classifying commits with transformers based on diffs

https://github.com/giganticode/diff-classifier

#### Identity merging

...



## BOHR-UI

BOHR-UI is a streamlit[1] app that visualizes the performance of different models in different projections. 

The app loads the data from 

- https://github.com/giganticode/bohr-workdir-bugginess
- https://github.com/giganticode/diff-classifier
- In the future, BOHR-UI could pull information from more data sources (from more BOHR working directories), and in different tabs, there can be visualizations of models for all the tasks that people are working on.

In theory, should be updated automatically once updates are pushed to the repositories.

Source code: https://github.com/giganticode/bohr-ui

BOHR-UI url: https://giganticode-bohr-ui-main-dev-j5tw3w.streamlitapp.com/

[1] The framework that allows developing data science visualization apps very quickly



## Future direction: working on SE heuristic API (aka BOHR API)

BOHR-API should allow heuristic developers quickly implement their heuristic ideas, like in the example below.

![image-20220704174314916](/Users/hlib/Library/Application Support/typora-user-images/image-20220704174314916.png)

## ideas and contributions of BOHR I've been trying to sell

- Facilitation of heuristic development (BOHR-API), would be a very important contribution, although this is 1) pretty much technical work and this is a lot of work - here we are not talking about 
- Reuse of heuristics: if there is a good API, won't it be easier to quickly implement new heuristics rather than share them? Jesus' comment: would the same heuristics work in different scenarios (for different projects), e.g. "fix" word heuristic will not work for the project where all issues start with "fix #..." - code in heuristics is what should be different for different researchers;
- debugging, integration, etc. - not something scientifically new, more technical, there is a mature Snorkel.ai that has these things implemented: the gap here might be support for heuristic development for software engineering (see the first bullet point)
- Storage of heuristics - if heuristics are not reused, for the sake of reproducibility, is a centralized repository needed? - BOHR runtime without centralized Bohr? - just an open-sourced snorkel flow?
- If we don't reuse heuristics there is not much need to agree on any label definitions -> only for dataset reuse.
- Reuse of label models: since heuristics cannot be reused for some projects -> label models cannot be reused easier; no need to reuse the model if there is a tool to quickly train it having implemented heuristics quickly.
- Reuse of datasets. 
- artifacts explorer

## BOHR demo (to be converted to one of tutorials)

First we create a separate virtual environment to make sure that the libraries used by BOHR do not clash with already installed libraries

```shell
pyenv virtualenv 3.8 bohr-demo
pyenv activate bohr-demo
pyenv which python
pip list
```



Now we install bohr-runtime. This will allow us to run BOHR commands. Besides, BOHR-API will be installed which will allow us to define a BOHR config

```
pip install bohr-runtime
```

Next, we clone a BOHR work-dir for the bugginess task, whose configuration is stored on Github

```
bohr clone https://github.com/giganticode/bohr-workdir-bugginess
```

If we try to reproduce the experiments, all the experiments will be up-to-date

```
cd bohr-workdir-bugginess

bohr repro
```

We can make changes to some heuristics and reproduce the experiments again

```
bohr repro
```



## Getting started with BOHR development

### BOHR repository

Source code: https://github.com/giganticode/bohr

This Github repo contains only the heuristics themselves (`heuristics` dir). For the BOHR engine, see BOHR-Runtime.

Heuristics are organized in a directory tree. Each file contains only one heuristic (exception is keyword heuristics marked with annotation `@KeywordHeuristics`). The name of the heuristic is the same as the name of the file. Heuristic files cannot depend on each other. Such organization allows to detect changes to which heuristics were made and need to be re-run.

If a file does not contain a function marked with `@Heuristic` decorator, such file will be ignored.  The type(s) of artifact(s) that heuristic can be applied to is passed as a parameter to the decorator. This allows the framework to know which artifact(s) the heuristic can be applied to.

 

### BOHR-runtime

Source code: https://github.com/giganticode/bohr-framework

#### Tests:

Most of the tests are implementing as doctests inside python docs strings for each method. This approach allows to keep the tests close to the code and to see how the code can be used. To run the doc test run:

```cd bohr-runtime && poetry run pytest --doctest-modules --ignore=test-b2b```

#### Project structure

............

├── Dockerfile    <- *creating a docker container with bohr installed to be deployed on CI server (github actions) - might be outdated*
├── bohrruntime <- *source code*
├── poetry.lock <- *file automatically generated by poetry (build and dependency management system for python)*
├── pyproject.toml <- *project config used by poetry*
├── renovate.json <- *renovate config (tool that automatically send PRs with updated dependencies)*
├── test <- *usual unit tests would go here (nothing here yet because we are using doctests all the time so far)*
└── test-b2b <- *b2b tests 2 simple scenarios to test the whole bohr workflow for labeling and grouping tasks*

#### Source code structure (bohrruntime directory)

bohrruntime
.................
├── appconfig.py <- *handling saving and loading values to/from BOHR config*
├── bohrconfig.py <- *code for parsing BOHR config*
├── cli 
│   ├── cli.py <- *implementation of cli commands like "bohr repro"*
│   ├── porcelain <- *implementation of internal cli commands used by pipeline manager (dvc) to execute stages*
│   └── remote
├── commands.py <- *implementation of CLI commands*
├── datamodel <- *implementation of main BOHR concepts*
│   ├── dataset.py
│   ├── experiment.py
│   ├── model.py
│   ├── task.py
│   └── bohrconfig.py
├── datasource.py <- *code related to loading datasets from Artifact Explorer* 
├── dvcwrapper.py <- *wrapper over dvc tool*
├── heuristics.py <- *code related to locating and loading heuristics*
├── pipeline.py <- *implements classes for each stage of pipeline and their convertion to pipeline manager config*
├── stages.py <- *implementation of stages of BOHR lifecycle without task-specific details*
├── storageengine.py <- *handles saving and loading of input and outputs of all stages to a (possibly virtual) file system*
├── tasktypes <- package containing task-specific logic
│   ├── filtering
│   ├── grouping
│   └── labeling
├── testtools.py <- *stub datamodel objects for testing*



### BOHR-labels

This is a dependency of BOHR-runtime

Source code: https://github.com/giganticode/bohr-labels

The label hierarchy can be extended by modifying text files under `labels`

In order for the hierarchy of objects that are used by heuristics to be updated according to the changes made to files in `labels`, `build/build.py` file has to be executed.

The file `bohrlabels/labels.py` will be updated.

### BOHR-API

This is another dependency of bohr-runtime.

Source code: https://github.com/giganticode/bohr-api



TODO ! different object hierarchies in Bohr-api and bohr-runtime



### Artifact Explorer

Source code can be found here: https://github.com/giganticode/commit-explorer

Commit explorer is the old name before we had a though to generalize the idea to all kinds of artifacts - not only commits. 

#### Mongo db 

Running on the ironspeed box (`10.10.20.160:27017`)

Connection string for read-only user: `mongodb://read-only-user:123@10.10.20.160:27017`

Username and password with write permissions please request from Hlib Babii

#### Http server

Artifact explorer is running an http server on the squirrel box (`squirrel.inf.unibz.it`)

TO check the status/restart the http-server, run on the squirrel box: 

`sudo systemctl status bohr-http`   /

`sudo systemctl restart bohr-http`

Running the service executes the following command: 

`/home/students/hbabii/.pyenv/versions/miniconda-3.7.0/bin/python -u /usr/local/web/bohr/run_bohr_server.py`

 `/usr/local/web/bohr/run_bohr_server.py` is a sim-link to `/home/students/hbabii/commit-explorer/server/server.py`

If some changes need to be made to the server code, push it to Github from your local machine then on the squirrel box:

`cd /home/students/hbabii/commit-explorer && git pull` then restart the service: `sudo systemctl restart bohr-http`

TODO example to access some commit

#### Crawler code overview

...



###  Bohr-workdir-bugginess:  bugginess task BOHR working directory

Github URL: https://github.com/giganticode/bohr-workdir-bugginess

#### Directory structure


├── bohr.lock
├── bohr.py  <- *bohr configuration*
├── cached-datasets <- *cached datasets, if dataset is absent in cache, it's reloaded from artifact explorer or from local path* 
│   ├── berger_files.jsonl
│   ├── berger_files.jsonl.metadata.json
│   ├── levin_files.jsonl
│   ├── levin_files.jsonl.metadata.json
│   ├── manual_labels.herzig.jsonl
│   ├── manual_labels.herzig.jsonl.metadata.json
│   ├── mauczka_files.jsonl
│   └── mauczka_files.jsonl.metadata.json
├── cloned-bohr <- *cloned bohr reprository of heuristics*
├── dvc.lock <- *dvc-managed file (for piprlinr management)*
├── dvc.yaml <-*dvc-managed file (for piprlinr management)*
└── runs <- *experiment results and files produced by intermediate stages*
    ├── \__heuristics
    │   ├── berger_files
    │   │   ├── bugginess. <- *results of heuristics applied to a dataset (berger_files) as part of the task (bugginess task)*
    .......
    ├── __single_heuristic_metrics
    │   ├── bugginess
    │   │   ├── berger_files  <- *metrics calculated for individual heuristics for the given task (bugginess) and the dataset (berger_files)*
	........
    ├── bugginess <- *experiment results for the bugginess task*
    │   ├── all_heuristics_with_issues <- *all_heuristics_with_issues experiment results*
    │   │   ├── berger_files <- *contains metrics of the given model for this dataset*
    │   │   ├── label_model.pkl <- *model file: this file is specific to the labeling task*
    │   │   ├── label_model_weights.csv <- *this file is specific to the labeling task*
    │   ├── random_model <- *baseline 1*
    │   │   ├── berger_files
    │   │   ├── manual_labels.herzig
    │   │   └── mauczka_files
    │   └── zero_model <- *baseline 2*
    │       ├── berger_files
    │       ├── manual_labels.herzig
    │       └── mauczka_files
	...



#### Default remote dataset and model storage

By default, when performing `bohr clone` , data will be pulled by http from http://squirrel.inf.unibz.it:8180 (the same server is shared with the artifact explorer, see #Artifact explorer - http server section)

When performing `bohr push` after the reproduction of the experiments, data will be pushed by ssh to ssh://squirrel.inf.unibz.it/data/bohr_dvc_storage. In order to perform the first push the credentials to the squirrel server has to be provided (unibz credentials) It can be done by running `bohr remote set-write-credentials <username> <password>`

This will add the username to `.dvc/config` and the password to `.dvc/config.local` files. The later one will be automatically gitignored so that it's not commited accidentally.



### BOHR-UI

Source code: https://github.com/giganticode/bohr-ui

Deployed app: https://giganticode-bohr-ui-main-nh18iq.streamlitapp.com/. (Streamlit server)

The app loads the data from 

- https://github.com/giganticode/bohr-workdir-bugginess
- https://github.com/giganticode/diff-classifier
- In the future, BOHR-UI could pull information from more data sources (from more BOHR working directories), and in different tabs, there can be visualizations of models for all the tasks that people are working on.

Data is updated automatically once updates are pushed to the repositories.





## TODOs, potential features, and ideas

- aggregate data from all experiments of the task





## TODO for these docs

Making sense of data - should be in bohr or UI

Tutorial - running experiments + makinf sense of data

Tutorial how to define a new task, how to add a new heuristics

Docs for each file

make things work when easily doable, if something doesn't mention in docs











