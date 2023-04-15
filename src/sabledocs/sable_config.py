from enum import Enum
from os import path
import tomllib


class RepositoryType(Enum):
    GITHUB = 1
    BITBUCKET = 2


class SableConfig:
    def __init__(self, config_file_path):
        self.module_title = "Module"
        self.footer_content = ""
        self.repository_url = ""
        self.repository_branch = ""
        self.repository_type = RepositoryType.GITHUB
        self.input_descriptor_file = "descriptor.pb"
        self.output_dir = "sabledocs_output"
        self.template = "_default"

        if path.exists(config_file_path):
            print(f"Configuration found in {config_file_path}")
            with open(config_file_path, mode='rb') as config_file:
                print("TOML file parsed")
                config_values = tomllib.load(config_file)
                print(config_values)
                if 'module-title' in config_values:
                    self.module_title = config_values['module-title']

                if 'input-descriptor-file' in config_values:
                    self.input_descriptor_file = config_values['input-descriptor-file']

                if 'output-dir' in config_values:
                    self.output_dir = config_values['output-dir'].rstrip("/\\")

                if 'template' in config_values:
                    self.template = config_values['template'].rstrip("/\\")

                if 'footer-content' in config_values:
                    self.footer_content = config_values['footer-content']

                if 'repository-url' in config_values:
                    self.repository_url = config_values['repository-url']

                if 'repository-branch' in config_values:
                    self.repository_branch = config_values['repository-branch']

                if 'repository-type' in config_values:
                    print("repository-type found")
                    match config_values['repository-type']:
                        case 'github':
                            self.repository_type = RepositoryType.GITHUB
                        case 'bitbucket':
                            self.repository_type = RepositoryType.BITBUCKET
        else:
            print("sabledocs.toml file not found, using default configuration.")
