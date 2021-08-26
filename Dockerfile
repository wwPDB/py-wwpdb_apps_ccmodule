FROM python:3.8 as builder

RUN apt-get update
RUN apt-get install -y bash libmariadb-dev libjpeg-dev zlib1g
RUN apt-get install -y cmake make git openssh-client gcc g++ musl-dev mariadb-client libffi-dev rustc cargo flex bison
RUN apt-get clean

# force using bash shell
SHELL ["/bin/bash", "-c"]

ARG CI_REGISTRY_USER
ARG CI_JOB_TOKEN
ARG CI_PROJECT_ID
ARG CI_REPOSITORY_PYPI_URL

ENV VENV=/venv
ENV PATH="$VENV/bin:$PATH"

RUN python -m venv $VENV

RUN pip config --site set global.extra-index-url https://${CI_REGISTRY_USER}:${CI_JOB_TOKEN}@${CI_REPOSITORY_PYPI_URL}/simple
RUN pip config --site set global.no-cache-dir false

# install guncorn for serving the wsgi scripts
RUN pip install --no-cache-dir wheel gunicorn

# install the depUI
WORKDIR /checkouts
COPY . .
RUN pip --no-cache-dir install .[server]


FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y bash libmariadb-dev
RUN apt-get clean

# force using bash shell
SHELL ["/bin/bash", "-c"]

ENV VENV=/venv
ENV PATH="$VENV/bin:$PATH"

WORKDIR ${VENV}
COPY --from=builder ${VENV} .

CMD ${SITE_CONFIG} && gunicorn wwpdb.apps.ccmodule.webapp.wsgi --bind 0.0.0.0:8000
