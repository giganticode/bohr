FROM ubuntu:18.04

WORKDIR /usr/src/bohr

MAINTAINER hlib <hlibbabii@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bc \
    build-essential \
    bzip2 \
    curl \
    git \
    libbz2-dev \
    libcairo2-dev \
    libffi-dev \
    libfontconfig-dev \
    libgif-dev \
    libjpeg-dev \
    liblzma-dev \
    libpango1.0-dev \
    libpython3-dev \
    librsvg2-dev \
    libsqlite3-dev \
    libssl-dev \
    openssl \
    p7zip-full \
    python-openssl

#cml
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash
RUN apt-get update
RUN apt-get install -y nodejs
RUN node -v
RUN npm -v

#RUN npm install -g vega-cli vega-lite
RUN npm i -g @dvcorg/cml

RUN unset PYENV_ROOT
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

ENV PATH="/root/.pyenv/bin:$PATH"

RUN pyenv install 3.8.0

COPY . .

ENV PYTHONPATH="/usr/src/bohr/:$PYTHONPATH"

RUN echo "$(ls)"
RUN /root/.pyenv/versions/3.8.0/bin/pip install Cython==0.29.21
RUN /root/.pyenv/versions/3.8.0/bin/pip install -r requirements.txt
RUN /root/.pyenv/versions/3.8.0/bin/python -c 'import nltk; nltk.download("punkt")'

RUN dvc --version

RUN apt-get install -y openjdk-11-jdk
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

RUN mkdir /usr/src/tools && cd /usr/src/tools && git clone https://github.com/tsantalis/RefactoringMiner
RUN cd /usr/src/tools/RefactoringMiner && ./gradlew distZip && ZIP_NAME="$(ls build/distributions)" && unzip "build/distributions/$ZIP_NAME" -d /usr/src/tools/
RUN ls /usr/src/tools/
RUN rm -rf /usr/src/tools/RefactoringMiner

RUN source /usr/src/bohr/config/env/docker.env

ENTRYPOINT ['/bin/bash']

