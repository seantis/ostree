import json

from cached_property import cached_property
from ostree import http
from ostree.remote import RemoteImage


# See https://stackoverflow.com/q/37861791
def parse_name(name):
    if '@' in name:
        name, digest = name.split('@')
    else:
        digest = None

    parts = name.split('/')

    if '/' in name and ('.' in parts[0] or ':' in parts[0]):
        host, parts = parts[0], parts[1:]
    else:
        host = None

    if ':' in parts[-1]:
        parts[-1], tag = parts[-1].split(':')
    else:
        tag = 'latest'

    repository = '/'.join(parts)
    return host, repository, tag, digest


class RemoteDockerImage(RemoteImage, name='docker'):

    def __init__(self, name):
        self.host, self.repository, self.tag, self.digest = parse_name(name)

    @cached_property
    def headers(self):
        url = (
            f'https://auth.docker.io/token'
            f'?service=registry.docker.io'
            f'&scope=repository:library/{self.repository}:pull'
        )

        token = json.loads(http.get(url))['token']

        return [
            f'Authorization: Bearer {token}',
            f'Accept: application/vnd.docker.distribution.manifest.v2+json'
        ]

    @cached_property
    def manifest(self):
        url = (
            f'https://registry-1.docker.io/v2/library/'
            f'{self.repository}/manifests/{self.tag}'
        )

        return json.loads(http.get(url, headers=self.headers))

    @property
    def latest_digest(self):
        return self.digest or self.manifest['config']['digest']

    @property
    def layers(self):
        return tuple(l['digest'] for l in self.manifest['layers'])

    def download_layer(self, layer, path):
        url = (
            f'https://registry-1.docker.io/v2/library/{self.repository}'
            f'/blobs/{layer}'
        )

        http.download(url, path, headers=self.headers)
