from enum import Enum
from os import path
import tomllib


class RepositoryType(Enum):
    NONE = 1
    GITHUB = 2
    BITBUCKET = 3


class SableConfig:
    def __init__(self, config_file_path):
        self.module_title = "Protobuf module documentation"
        self.input_descriptor_file = "descriptor.pb"
        self.template = "_default"
        self.footer_content = ""
        self.main_page_content_file = ""
        self.output_dir = "sabledocs_output"
        self.enable_lunr_search = True
        self.repository_url = ""
        self.repository_branch = ""
        self.repository_type = RepositoryType.NONE

        if path.exists(config_file_path):
            print(f"Configuration found in {config_file_path}")
            with open(config_file_path, mode='rb') as config_file:
                config_values = tomllib.load(config_file)

                self.module_title = config_values.get('module-title', self.module_title)

                self.input_descriptor_file = config_values.get('input-descriptor-file', self.input_descriptor_file)

                self.template = config_values.get('template', self.template).rstrip("/\\")

                self.footer_content = config_values.get('footer-content', self.footer_content)

                self.main_page_content_file = config_values.get('main-page-content-file', self.main_page_content_file)

                self.output_dir = config_values.get('output-dir', self.output_dir).rstrip("/\\")

                self.enable_lunr_search = config_values.get('enable-lunr-search', True)

                self.repository_url = config_values.get('repository-url', self.repository_url)

                self.repository_branch = config_values.get('repository-branch', self.repository_branch)

                if 'repository-type' in config_values:
                    match config_values['repository-type']:
                        case 'github':
                            self.repository_type = RepositoryType.GITHUB
                        case 'bitbucket':
                            self.repository_type = RepositoryType.BITBUCKET
        else:
            print("sabledocs.toml file not found, using default configuration.")
