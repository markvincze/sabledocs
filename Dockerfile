FROM python:3.12.0

ARG sabledocs_version
ARG protoc_version

RUN apt update && \
    apt install -y jq && \
    #protoc_version=$(curl -sL https://api.github.com/repos/protocolbuffers/protobuf/releases/latest | jq -r ".tag_name") && \
    wget https://github.com/protocolbuffers/protobuf/releases/download/v${protoc_version}/protoc-${protoc_version}-linux-x86_64.zip && \
    unzip -q protoc-${protoc_version}-linux-x86_64.zip -d ./protoc && \
    cp ./protoc/bin/protoc /bin && \
    pip install sabledocs==${sabledocs_version}

    #wget https://github.com/protocolbuffers/protobuf/releases/download/${protoc_version}/protoc-${protoc_version:1}-linux-x86_64.zip
    #unzip -q protoc-${protoc_version}-linux-x86_64.zip -d ./protoc && \
    #cp ./protoc/bin/protoc /bin && \
    #pip install sabledocs==${sabledocs_version}
