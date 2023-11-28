import json
import markdown
import os
import pprint
import sys
from shutil import copytree, rmtree

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sabledocs.lunr_search import build_search_index
from sabledocs.proto_descriptor_parser import parse_proto_descriptor
from sabledocs.sable_config import SableConfig


def check_python_version():
    print(f"Python {sys.version}")

    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 11):
        print("WARNING: Sabledocs requires Python version 3.11 or higher")


def cli():
    print("Starting Sabledocs")
    check_python_version()

    print()
    print("Starting documentation generation.")
    sable_config = SableConfig("sabledocs.toml")

    if not os.path.exists(sable_config.input_descriptor_file):
        print()
        print(f'ERROR: The Proto descriptor file {sable_config.input_descriptor_file} does not exist. Exiting.')
        return

    # Execute the main processing of the Proto contracts.
    sable_context = parse_proto_descriptor(sable_config)

    if sable_config.template != "_default":
        print()
        print('WARNING: The "template" config parameter is deprecated, it will be removed in a future version. The field template-path should be used instead.')
        template_base_dir = f"templates/{sable_config.template}"
    else:
        template_base_dir = sable_config.template_path if sable_config.template_path else os.path.join(os.path.dirname(__file__), "templates", "_default")

    jinja_env = Environment(
        loader=FileSystemLoader(searchpath=template_base_dir),
        autoescape=select_autoescape()
    )

    package_template = jinja_env.get_template("package.html")

    if not os.path.exists(sable_config.output_dir):
        os.makedirs(sable_config.output_dir)

    # NOTE: When the output files are generated, the encode('utf-8') option has to be used, otherwise Unicode characters like © can end up garbled.
    for package in sable_context.packages:
        with open(os.path.join(sable_config.output_dir, f'{package.name if package.name else "__default"}.html'), 'wb') as fh:
            output = package_template.render(
                sable_config=sable_config,
                package=package,
                packages=sable_context.packages,
                non_hidden_packages=sable_context.non_hidden_packages,
                all_messages=sable_context.all_messages,
                all_enums=sable_context.all_enums).encode('utf-8')

            fh.write(output)

    main_page_content = ""

    if sable_config.main_page_content_file != "":
        print()
        if os.path.exists(sable_config.main_page_content_file):
            print(f"Found main content page, {sable_config.main_page_content_file}.")
            with open(sable_config.main_page_content_file, mode='r') as main_page_content_file:
                main_page_content = markdown.markdown(main_page_content_file.read(), extensions=['fenced_code'])
        else:
            print(f"WARNING: The configured main content page, {sable_config.main_page_content_file} was not found.")

    with open(os.path.join(sable_config.output_dir, 'index.html'), 'wb') as fh:
        output = jinja_env.get_template("index.html").render(
            sable_config = sable_config,
            main_page_content = main_page_content,
            packages = sable_context.packages,
            non_hidden_packages=sable_context.non_hidden_packages,
            all_messages = sable_context.all_messages,
            all_enums = sable_context.all_enums).encode('utf-8')

        fh.write(output)

    output_static_path = os.path.join(sable_config.output_dir, "static")

    if os.path.exists(output_static_path):
        # This is needed, because shutils.copytree cannot copy to a target folder which already exists.
        rmtree(output_static_path)

    copytree(os.path.join(template_base_dir, "static"), output_static_path)

    if sable_config.enable_lunr_search:
        (search_documents, search_index) = build_search_index(sable_context)

        with open(os.path.join(sable_config.output_dir, 'search.html'), 'wb') as fh:
            output = jinja_env.get_template("search.html").render(
                sable_config = sable_config,
                search_documents = json.dumps(search_documents),
                search_index = json.dumps(search_index.serialize())).encode('utf-8')

            fh.write(output)

    index_abs_path = os.path.abspath(os.path.join(sable_config.output_dir, "index.html"))

    print()
    print(f"Building documentation done. It can be opened with {index_abs_path}")

if __name__ == '__main__':  # pragma: no cover
    cli()
