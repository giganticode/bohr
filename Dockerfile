FROM dvcorg/cml-py3:latest

WORKDIR /usr/src/bohr

MAINTAINER hlib <hlibbabii@gmail.com>

COPY . .

RUN sudo apt-get update && sudo apt-get install libpython3-dev p7zip-full bzip2 openssl libssl-dev libffi-dev liblzma-dev python-openssl libbz2-dev libsqlite3-dev

RUN unset PYENV_ROOT
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

ENV PATH="/root/.pyenv/bin:$PATH"
ENV PYTHONPATH="/usr/src/bohr/:$PYTHONPATH"

RUN pyenv install 3.8.0

RUN echo "$(ls)"
RUN /root/.pyenv/versions/3.8.0/bin/pip install Cython==0.29.21
RUN /root/.pyenv/versions/3.8.0/bin/pip install -r requirements.txt
RUN /root/.pyenv/versions/3.8.0/bin/python -c 'import nltk; nltk.download("punkt")'

RUN dvc --version
RUN dvc pull downloaded-data/smells-madeyski.csv.dvc

ENTRYPOINT ['/bin/bash']
