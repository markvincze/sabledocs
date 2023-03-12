from enum import Enum


class RepositoryType(Enum):
    GITHUB = 1
    BITBUCKET = 2


class SableConfig:
    def __init__(self):
        self.footer_content = ''
        self.repository_url = ''
        self.repository_branch = 'main'
        self.repository_type = RepositoryType.GITHUB
