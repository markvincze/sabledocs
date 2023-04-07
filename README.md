# sable-docs

Generate Proto descriptor:

```
protoc .\google\datastore\v1\*.proto -o datastore.pb --include_source_info
```

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
pip install ../sabledocs
```
