import json
import pprint
from proto_descriptor_parser import parse_proto_descriptor
from jinja2 import Environment, FileSystemLoader, select_autoescape

# packages = parse_proto_json('description.json')
packages = parse_proto_descriptor('descriptor.pb')


#pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(packages)

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape()
)

#template = jinja_env.get_template('templates/docs.html.jinja')
template = jinja_env.get_template('templates/package.html.jinja')

for package in packages:
    print('Enums:')
    print(package.enums)
    with open(f'{package.name}.html', 'w') as fh:
        fh.write(template.render(package=package, packages=packages))

# print(template.render(package=packages[1], packages=packages))
