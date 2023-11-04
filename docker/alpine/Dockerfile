FROM python:3.12.0-alpine

ARG sabledocs_version

RUN apk update && \
    apk add protoc && \
    pip install sabledocs==${sabledocs_version}
