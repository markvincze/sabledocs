import unittest

from sabledocs.sable_config import RepositoryType
from sabledocs.proto_descriptor_parser import build_source_code_url

class TestProtoDescriptorParser(unittest.TestCase):

    def test_code_url_github_style(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.GITHUB,
                "main",
                "", # no repository_dir
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/blob/main/foo/bar.proto#L42'

        self.assertEqual(got, expected)

    def test_code_url_github_style_with_repo_dir(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.GITHUB,
                "main",
                "myrepodir",
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/blob/main/myrepodir/foo/bar.proto#L42'

        self.assertEqual(got, expected)

    def test_code_url_github_style_extra_slashes(self):

        got = build_source_code_url(
                'https://git.example.com/',
                RepositoryType.GITHUB,
                "main",
                "/myrepodir/",
                "/foo/bar.proto",
                41)

        expected = 'https://git.example.com/blob/main/myrepodir/foo/bar.proto#L42'

        self.assertEqual(got, expected)

    def test_code_url_bitbucket_style(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.BITBUCKET,
                "main",
                "", # no repository_dir
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/src/main/foo/bar.proto#lines-42'

        self.assertEqual(got, expected)

    def test_code_url_bitbucket_style_with_repo_dir(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.BITBUCKET,
                "main",
                "myrepodir",
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/src/main/myrepodir/foo/bar.proto#lines-42'

        self.assertEqual(got, expected)

    def test_code_url_bitbucket_style_extra_slashes(self):

        got = build_source_code_url(
                'https://git.example.com/',
                RepositoryType.BITBUCKET,
                "main",
                "/myrepodir/",
                "/foo/bar.proto",
                41)

        expected = 'https://git.example.com/src/main/myrepodir/foo/bar.proto#lines-42'

        self.assertEqual(got, expected)

    def test_code_url_gitlab_style(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.GITLAB,
                "main",
                "", # no repository_dir
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/-/blob/main/foo/bar.proto#L41'

        self.assertEqual(got, expected)

    def test_code_url_gitlab_style_with_repo_dir(self):

        got = build_source_code_url(
                'https://git.example.com',
                RepositoryType.GITLAB,
                "main",
                "myrepodir",
                "foo/bar.proto",
                41)

        expected = 'https://git.example.com/-/blob/main/myrepodir/foo/bar.proto#L41'

        self.assertEqual(got, expected)

    def test_code_url_gitlab_style_extra_slashes(self):

        got = build_source_code_url(
                'https://git.example.com/',
                RepositoryType.GITLAB,
                "main",
                "/myrepodir/",
                "/foo/bar.proto",
                41)

        expected = 'https://git.example.com/-/blob/main/myrepodir/foo/bar.proto#L41'

        self.assertEqual(got, expected)
