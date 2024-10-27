# MAINTAINER rec
ARG CI_ARTIFACTORY_URL_CLOUD_BASE
FROM $CI_ARTIFACTORY_URL_CLOUD_BASE/python:3.8-slim

ENV PROJECT_ROOT="/opt/description-of-databases"
ENV PYTHONPATH=${PYTHONPATH}:${PROJECT_ROOT}

WORKDIR ${PROJECT_ROOT}

ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL

COPY requirements.txt requirements.txt

RUN pip --no-cache-dir install -U -r requirements.txt && \
    rm -rf /tmp/*

ADD . ./

EXPOSE 8000
