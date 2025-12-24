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
# They are used to generate deeplinks for the members of the Proto model pointing to the original source
# code. By default these fields are not configured, and source code links are not included in the docs.
# The repository-type field supports the following possible values, "github", "bitbucket", "bitbucket-data-center" and "gitlab".
# The fields repository-url and repository-branch should be configured to point to the correct repository.
# repository-dir should be set only if the root of your Protobuf module is in a specific directory inside your repository.
repository-type = "github"
repository-url = "https://github.com/janedoe/myawesomeproject"
repository-branch = "main"
repository-dir = "proto"

# In each comment, ignore everything that comes after (until end of the comment) one of the keywords.
# Default value: []
ignore-comments-after = ["@exclude"]
# In each comment, ignore all lines that contain at least one keyword from the following list.
# Default value: []
ignore-comment-lines-containing = ["buf:lint"]

# Packages can be hidden from the generated documentation by adding them to the hidden-packages
# collection. In the templates, the field non_hidden_packages can be used to access the packages which are
# not listed in hidden-packages. (And the packages field returns all packages.)
# Default value: []
hidden-packages = ["google.protobuf"]

# By default, packages and members in a package are ordered alphabetically.
# By setting the member-ordering option to "preserve", the original order present in the Protobuf
# definitions will be preserved.
# When using the "preserve" option and having multiple proto input files, the order of the members will
# depend not just on the physical order in the Protobuf files, but also on the order in which the files
# were listed in the input when `protoc` was executed.
# Default value: ""
member-ordering = "preserve"

# The markdown extensions supported by the main-page-content-file
# Default value: ["fenced_code"]
# See: https://python-markdown.github.io/extensions/#officially-supported-extensions
markdown-extensions = ["fenced_code", "nl2br"]

```

### Main page content

Custom introduction content can be specified in a separate file, which can be displayed above the packages list on the main page of the documentation.  
Then the name of the file has to be specified in the `main-page-content-file` configuration setting.

```toml
main-page-content-file = "intro.md"
```

See the example on the main page of the [demo site](https://markvincze.github.io/sabledocs/demo/).

### Static content

Extra static content, such as additional HTML files or images can be included in the generated output by creating a directory called `static` next to the `sabledocs.toml` file, and copying the static files there.
All the files inside the `static` folder will be copied to the _root_ of the generated output (so there won't be a `static` subfolder created).

### Markdown support

Markdown can be used both in the main content page, and also in the Protobuf comments.  
Code blocks can be defined both with indentation, and with the ``` fence.

```
// These are the comments for SearchRequest
//
// ```
// namespace Test
// {
//     public class Foo {
//         public string Bar { get; set; }
//     }
// }
// ```
message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 results_per_page = 3;
}
```

(If you include code blocks in a comment, then it's better to use single-line comments (`// ...`) as opposed to block comments (`/* ... */`), because the `protoc` compiler trims all leading whitespace from the lines in block comments, thus the indentation in code blocks gets lost.)

### Customize Jinja templates for primary content

The `template-path` configuration parameter can be used to specify an alternative directory where the Jinja templates that drive the content of Sabledocs can be found.
Copy the contents of the `src/sabledocs/templates/_default` from the current version of Sabledocs to the configured directory then edit the templates as necessary. 

```toml
template-path = "templates"
```

### Extra Jinja templates

If you would like to include your own Jinja templates, specify the `extra-template-path` configuration parameter and
all files that end in `extra-template-suffix` (default ".html") will be processed and included as a Jinja template in the output
path at a location relative to the `extra-template-path`.

Also processes all subdirectories of `extra-template-path` recursively.  

Prefix a subdirectory with `_` to have it ignored.

```toml
extra-template-path = "extra-templates"
extra-template-suffix = ".tpl" # default value is ".html"
```

### Custom Parsing of Comments

In some cases, it may be desirable to implement additional processing on the comment strings before inserting them into the HTML document.

PLEASE NOTE: This is an advanced feature that some have used to embed additional machine-parseable information into a `.proto` file.
Users should be aware that use of this feature will probably make it harder to formatting options that `sabledocs` implements, especially those that are white-space sensitive.

It is activated by indicating a python script defining a class that inherits from [CommentsParser](src/sabledocs/comments_parser.py).
This class will be instantiated by `sabledocs` and its methods invoked to pre-process the comment strings that have been collected for
Messages, Fields, Enums, EnumValues, Services, and ServiceMethods.
Or, processing of all of these different entities can be indicate by reimplementing `CommentsParser.ParseAll()`.

An example of using this feature to process comments formatted as JSON strings can be found at [custom_comments_parser.py](sample/custom_comments_parser.py).

```toml
comments-parser-file = "sample/custom_comments_parser.py"
```

### Using with Docker

For convenient usage in CI builds and other scenarios where a Docker image is preferable, the image [`markvincze/sabledocs`](https://hub.docker.com/r/markvincze/sabledocs) can be used, which has both the `protoc` CLI, and `sabledocs` preinstalled.

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
pip install -e .
```

Build the library and the sample documentation, from the `sample` folder:

```
# PowerShell
npm run css-build; pip install ..; sabledocs; .\output\index.html

# Bash
npm run css-build && pip install .. && sabledocs && .\output\index.html
```
