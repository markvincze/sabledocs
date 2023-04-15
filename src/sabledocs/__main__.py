import pprint
import os
from distutils.dir_util import copy_tree
from re import template
from sabledocs.proto_descriptor_parser import parse_proto_descriptor
from sabledocs.sable_config import SableConfig
from jinja2 import Environment, FileSystemLoader, select_autoescape


def cli():
    print("Starting documentation generation.")
    sable_config = SableConfig("sabledocs.toml")

    sable_context = parse_proto_descriptor(sable_config)

    template_base_dir = os.path.join(os.path.dirname(__file__), "templates", "_default") if sable_config.template == "_default" else f"templates/{sable_config.template}"

    jinja_env = Environment(
        loader=FileSystemLoader(searchpath=template_base_dir),
        autoescape=select_autoescape()
    )

    package_template = jinja_env.get_template("package.html")

    if not os.path.exists(sable_config.output_dir):
        os.makedirs(sable_config.output_dir)

    for package in sable_context.packages:
        with open(os.path.join(sable_config.output_dir, f'{package.name}.html'), 'wb') as fh:
            output = package_template.render(
                sable_config=sable_config,
                package=package,
                packages=sable_context.packages,
                all_messages=sable_context.all_messages,
                all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

            fh.write(output)

    with open(os.path.join(sable_config.output_dir, 'index.html'), 'wb') as fh:
        output = jinja_env.get_template("index.html").render(
            sable_config = sable_config,
            packages=sable_context.packages,
            all_messages=sable_context.all_messages,
            all_enums=sable_context.all_enums).encode('utf-8') # Without encode('utf-8'), Unicode characters like © ended up garbled.

        fh.write(output)

    copy_tree(os.path.join(template_base_dir, "static"), os.path.join(sable_config.output_dir, "static"))

    index_abs_path = os.path.abspath(os.path.join(sable_config.output_dir, "index.html"))
    print(f"Building documentation done. It can be opened with {index_abs_path}")

if __name__ == '__main__':  # pragma: no cover
    cli()
