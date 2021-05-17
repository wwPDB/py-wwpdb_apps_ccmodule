FROM python:3.8-alpine as builder

RUN apk add --update --no-cache cmake make git openssh openssl-dev bash gcc g++ musl-dev linux-headers libressl-dev libffi-dev rust cargo flex bison mariadb-dev mariadb-connector-c mariadb-connector-c-dev

# force using bash shell
SHELL ["/bin/bash", "-c"]

ARG CI_REGISTRY_USER
ARG CI_JOB_TOKEN
ARG CI_PROJECT_ID
ARG CI_REPOSITORY_PYPI_URL

ENV ONEDEP_PATH=/wwpdb/onedep
ENV SITE_CONFIG_PATH=${ONEDEP_PATH}/site-config
ENV VENV=$ONEDEP_PATH/venv
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


FROM python:3.8-alpine

RUN apk add --update --no-cache bash mariadb-connector-c mariadb-connector-c-dev

# force using bash shell
SHELL ["/bin/bash", "-c"]

ENV ONEDEP_PATH=/wwpdb/onedep
ENV VENV=$ONEDEP_PATH/venv
ENV PATH="$VENV/bin:$PATH"

ENV SITE_CONFIG='. ${TOP_WWPDB_SITE_CONFIG_DIR}/init/env.sh --siteid ${WWPDB_SITE_ID} --location ${WWPDB_SITE_LOC}'
ENV WRITE_SITE_CONFIG_CACHE='ConfigInfoFileExec --siteid $WWPDB_SITE_ID --locid $WWPDB_SITE_LOC --writecache'

WORKDIR ${ONEDEP_PATH}
COPY --from=builder ${ONEDEP_PATH} .

# allow apache to come through
EXPOSE 25 80 465 587 443 5672 5673 8000

CMD ${SITE_CONFIG} && gunicorn wwpdb.apps.ccmodule.webapp.wsgi --bind 0.0.0.0:8000
