import json
import pprint
from proto_descriptor_parser import parse_proto_descriptor
from sable_config import RepositoryType
from sable_config import SableConfig
from jinja2 import Environment, FileSystemLoader, select_autoescape

sable_config = SableConfig("sable.toml")

sable_context = parse_proto_descriptor('descriptor.pb', sable_config)
# sable_context = parse_proto_descriptor('pubsub.pb', sable_config)
#sable_context = parse_proto_descriptor('sable-test.pb')
#sable_context = parse_proto_descriptor('datastore.pb', sable_config)

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape()
)

package_template = jinja_env.get_template('templates/package.html')

for package in sable_context.packages:
    with open(f'{package.name}.html', 'wb') as fh:
        output = package_template.render(
            sable_config = sable_config,
            package=package,
            packages=sable_context.packages,
            all_messages=sable_context.all_messages,
            all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

        fh.write(output)

with open('index.html', 'wb') as fh:
    output = jinja_env.get_template('templates/index.html').render(
        sable_config = sable_config,
        packages=sable_context.packages,
        all_messages=sable_context.all_messages,
        all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

    fh.write(output)
