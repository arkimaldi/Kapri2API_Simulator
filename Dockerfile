# Build-time variables.
ARG DEBIAN_RELEASE=bullseye
ARG PYTHON_VER=3.9
ARG PYINSTALLER_VER=6.1.0
ARG PIP_TOOLS_VER=6.8.0
ARG FPM_VER=1.14.2
ARG PYTEST_VER=7.0.1
# rchardet requires Ruby version >= 3.0.0.
ARG RUBY_RCHARDET_VER=1.8.0
# Ruby package git >=1.12 requires Ruby >=2.6 (not available in Debian 9)
ARG RUBY_GIT_VER=1.11.0
# Ruby package rexml ver 3.2.6 requires Ruby version >= 2.5.0
ARG RUBY_REXML_VER=3.2.4

## Base Image ##
FROM python:$PYTHON_VER-slim-$DEBIAN_RELEASE AS base

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install pip-compile.
ARG PIP_TOOLS_VER
RUN pip install --no-cache-dir \
    pip-tools==$PIP_TOOLS_VER

## End Base Image ##

## Builder Image ##
FROM base AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NOWARNINGS=yes

# Install system tools needed by fpm and pyinstaller.
## RUN echo "deb http://archive.debian.org/debian stretch main" > /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    ruby \
    gcc \
    g++ \
    binutils \
    linux-libc-dev \
    zlib1g-dev \
    libjpeg-dev \
    libtk8.6

# Install FPM.
ARG RUBY_RCHARDET_VER
ARG RUBY_GIT_VER
ARG RUBY_REXML_VER
ARG FPM_VER
RUN gem install rchardet -v $RUBY_RCHARDET_VER
RUN gem install git -v $RUBY_GIT_VER
RUN gem install rexml -v $RUBY_REXML_VER
RUN gem install fpm -v $FPM_VER

# Log Ruby installed dependencies
RUN gem dependency

# Install pyinstaller.
ARG PYINSTALLER_VER
ARG PYTEST_VER
RUN pip install --no-cache-dir \
    pyinstaller==$PYINSTALLER_VER \
    pytest==$PYTEST_VER

# Install program dependencies.
COPY requirements.txt /work/
WORKDIR /work

RUN pip install -r requirements.txt

# Copy source files.
ADD debian /work/debian/
ADD src /work/src/
ADD config /work/config/

## End Builder Image ##

