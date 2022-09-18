## Reproducing Experiments

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

