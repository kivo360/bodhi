FROM tiangolo/uvicorn-gunicorn:python3.8

LABEL maintainer="Kevin Hill <kevin@insync.systems>"

COPY ./requirements.txt  /app/

# RUN apt-get install graphviz graphviz-dev -y
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz graphviz-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pyparsing pydot

RUN pip install graphviz pygraphviz
RUN pip install -r requirements.txt

ENV MODULE_NAME="bodhi_service.service.app"

COPY ./bodhi_service /app/bodhi_service