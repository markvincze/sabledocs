# [Sabledocs](https://markvincze.github.io/sabledocs/)

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/markvincze/sabledocs/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/markvincze/sabledocs/tree/main)
[![PyPi](https://img.shields.io/pypi/v/sabledocs.svg)](https://pypi.org/project/sabledocs/)
[![Python versions](https://img.shields.io/pypi/pyversions/sabledocs.svg)](https://pypi.org/project/sabledocs/)

A simple static documentation generator for Protobuf and gRPC contracts.

**Demo**: You can check out this [demo](https://markvincze.github.io/sabledocs/demo/) showing the generated documentation for some of the [Google Cloud SDK contracts](https://github.com/googleapis/googleapis/tree/master/google/pubsub/v1).

## How to use

### Generate the proto descriptor

In order to build the documentation, you need to generate a binary descriptor from your Proto contracts using `protoc`. If you don't have it yet, the `protoc` CLI can be installed by downloading the release from the official [protobuf](https://github.com/protocolbuffers/protobuf/releases) repository.

For example in the folder where your proto files are located, you can execute the following command.

```
protoc *.proto -o descriptor.pb --include_source_info
```

*(It's important to use the `--include_source_info` flag, otherwise the comments will not be included in the generated documentation.)*

The generated `descriptor.pb` file will be the input needed to build the documentation site.

### Build the documentation

Install the `sabledocs` package. It requires [Python](https://www.python.org/downloads/) (version 3.11 or higher) to be installed.

```
pip install sabledocs
```

In the same folder where the generated `descriptor.pb` file is located, execute the command.

```
sabledocs
```

The documentation will be generated into a folder `sabledocs_output`, its main page can be opened with `index.html`.

### Customization

For further customization, create a `sabledocs.toml` file in the folder where the Protobuf descriptor file is located and from which the `sabledocs` CLI is executed.
You can customize the following options. Any omitted field will use its default value.

```toml
# Configures the main title of the documentation site.
# Default value: "Protobuf module documentation"
module-title = "My Awesome Module"

# Specifies the name of the Protobuf descriptor file.
# Default value: "descriptor.pb"
input-descriptor-file = "myawesomemodule.pb"

# Specifies the file which contains the content to display on the main page above the package list.
# Default value: ""
main-page-content-file = "intro.md"

# The output folder to which the documentation is generated.
# Default value: "sabledocs_output"
output-dir = "docs"

# Controls whether the the search functionality is enabled with a prebuilt Lunr index.
# Default value: true
enable-lunr-search = true

# Copyright message displayed in the footer.
# Default value: ""
footer-content = "© 2023 Jane Doe. All rights reserved."

# The following 3 fields configure the source control repository of the project.
# It is used to generate deeplink for the components of the Proto model pointing to the original source code.
# By default these fields are not configured, and source code links are not included in the docs.
# The repository-type field supports two possible values, "github" and "bitbucket".
# The fields repository-url and `repository-branch` should be configured to point to the correct repository.
repository-type = "github"
repository-url = "https://github.com/janedoe/myawesomeproject"
repository-branch = "main"
```

#### Main page content

Custom introduction content can be specified in a separate file, which can be displayed above the packages list on the main page of the documentation.  
Then the name of the file has to be specified in the `main-page-content-file` configuration setting.

```toml
main-page-content-file = "intro.md"
```

See the example on the main page of the [demo site](https://markvincze.github.io/sabledocs/demo/).

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
