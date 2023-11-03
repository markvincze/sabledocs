FROM python:3.12.0-alpine

ARG sabledocs_version

RUN apk update && \
    apk add protobuf && \
    pip install sabledocs==${sabledocs_version}
