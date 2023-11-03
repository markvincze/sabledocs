FROM python:3.12.0-alpine

ARG sabledocs_version
ARG protoc_version

RUN apk update && \
    apk add jq && \
    wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protoc-${protoc_version}-linux-x86_64.zip && \
    unzip -q protoc-${protoc_version}-linux-x86_64.zip -d ./protoc && \
    cp ./protoc/bin/protoc /bin && \
    pip install sabledocs==${sabledocs_version}
