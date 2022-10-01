import json
import pprint
from proto_descriptor_parser import parse_proto_descriptor
from jinja2 import Environment, FileSystemLoader, select_autoescape

packages = parse_proto_descriptor('descriptor.pb')

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape()
)

template = jinja_env.get_template('templates/package.html')

for package in packages:
    print('Enums:')
    print(package.enums)
    with open(f'{package.name}.html', 'w') as fh:
        fh.write(template.render(package=package, packages=packages))

