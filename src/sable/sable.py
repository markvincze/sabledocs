import json
import pprint
from distutils.dir_util import copy_tree
from proto_descriptor_parser import parse_proto_descriptor
from sable_config import SableConfig
from jinja2 import Environment, FileSystemLoader, select_autoescape
from os import path

sable_config = SableConfig("sable.toml")

# sable_context = parse_proto_descriptor('descriptor.pb', sable_config)
# sable_context = parse_proto_descriptor('pubsub.pb', sable_config)
# sable_context = parse_proto_descriptor('sable-test.pb')
sable_context = parse_proto_descriptor('datastore.pb', sable_config)

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape()
)

package_template = jinja_env.get_template(f"templates/{sable_config.template}/package.html")

for package in sable_context.packages:
    with open(path.join(sable_config.output_dir, f'{package.name}.html'), 'wb') as fh:
        output = package_template.render(
            sable_config = sable_config,
            package=package,
            packages=sable_context.packages,
            all_messages=sable_context.all_messages,
            all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

        fh.write(output)

with open(path.join(sable_config.output_dir, 'index.html'), 'wb') as fh:
    output = jinja_env.get_template(f"templates/{sable_config.template}/index.html").render(
        sable_config = sable_config,
        packages=sable_context.packages,
        all_messages=sable_context.all_messages,
        all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

    fh.write(output)

copy_tree(f"templates/{sable_config.template}/static", path.join(sable_config.output_dir, "static"))
