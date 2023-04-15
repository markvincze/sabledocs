# sabledocs

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/markvincze/sabledocs/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/markvincze/sabledocs/tree/main)

A simple static documentation generator for Protobuf and gRPC contracts.

## How to use

### Generate the proto descriptor

In order to build the documentation, you need to generate a binary descriptor from your Proto contracts using `protoc`. If you don't have it yet, the `protoc` CLI can be installed by downloading the release from the official [protobuf](https://github.com/protocolbuffers/protobuf/releases) repository.

For example in the folder where your proto files are located, you can execute the following command.

```
protoc *.proto -o descriptor.pb --include_source_info
```

*(It's important to use the `--include_source_info` flag, otherwise the comments will not be included in the generated documentation.)*

The generated `descriptor.pb` file will be the input needed to build the documentation site.

### Build the documetation

Install the `sabledocs` package.

```
pip install sabledocs
```

In the same folder where the generated `descriptor.pb` file is located, execute the command.

```
sabledocs
```

The documentation will be generated into a folder `sabledocs_output`, its main page can be opened with `index.html`.

## For maintainers

Build the Python package:

```
python -m build
```

Publish with twine:

```
python -m twine upload --repository testpypi dist/*
```

Install from the local folder:

```
pip install .
```
