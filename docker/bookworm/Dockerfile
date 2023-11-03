FROM python:3.12.0-bookworm

ARG sabledocs_version
ARG protoc_version

RUN apt update && \
    apt install -y jq && \
    wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protoc-${protoc_version}-linux-x86_64.zip && \
    unzip -q protoc-${protoc_version}-linux-x86_64.zip -d ./protoc && \
    cp ./protoc/bin/protoc /bin && \
    pip install sabledocs==${sabledocs_version}
