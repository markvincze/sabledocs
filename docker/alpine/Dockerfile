FROM python:3.12-alpine

ARG sabledocs_version

RUN apk update && \
    apk add protobuf-dev && \
    pip install sabledocs==${sabledocs_version}
