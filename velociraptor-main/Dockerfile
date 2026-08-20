ARG BASE_IMAGE=cdn.harbor.global.lmco.com/lmc.eo.swf.internal/python
ARG BASE_TAG=v2
ARG EFOSS_USER
ARG EFOSS_TOKEN
ARG CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ARG SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ARG PYPI_USERNAME
ARG PYPI_TOKEN

FROM $BASE_IMAGE:$BASE_TAG
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG EFOSS_USER
ARG EFOSS_TOKEN
ARG CURL_CA_BUNDLE
ARG SSL_CERT_FILE
ARG PYPI_USERNAME
ARG PYPI_TOKEN

COPY velociraptor ./velociraptor
COPY requirements.txt velociraptor\requirements.txt

RUN export PIP_TRUSTED_HOST="nexus.global.lmco.com nexus-ent.us.lmco.com" \
    && echo Installing virtual environment \
    && virtualenv venv \
    && pip config set global.cert /usr/local/share/ca-certificates/ca-certificates.crt \
    && pip config set global.index-url https://$EFOSS_USER:$EFOSS_TOKEN@nexus.global.lmco.com/repository/pypi-proxy/simple/ \
    && pip config set global.extra-index-url https://$EFOSS_USER:$EFOSS_TOKEN@nexus.global.lmco.com/repository/swf-pypi/simple/ \
    && source venv/bin/activate \
    && pip install -r velociraptor\requirements.txt

COPY run_compare_sheet.bat .
CMD ["run_compare_sheet.bat"]

