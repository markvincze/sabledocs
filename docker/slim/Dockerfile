FROM python:3.12.0-slim

ARG sabledocs_version

RUN apt update && \
    apt install -y protobuf-compiler && \
    pip install sabledocs==${sabledocs_version}
