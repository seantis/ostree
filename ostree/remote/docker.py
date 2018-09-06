import requests

from cached_property import cached_property
from google.auth.transport.requests import AuthorizedSession
from ostree.remote import RemoteAuth, RemoteImage
from google.oauth2.service_account import Credentials


class DockerIdentity(object):

    __slots__ = ('name', 'host', 'repository', 'tag', 'digest')

    def __init__(self, host, repository, tag, digest):
        self.host = host
        self.repository = repository
        self.tag = tag
        self.digest = digest

    @classmethod
    def from_name(cls, name):
        # See https://stackoverflow.com/q/37861791
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

        return cls(host, repository, tag, digest)


class PublicDockerAuth(RemoteAuth, hosts=(None, )):

    def create_session(self, auth):
        token = auth or self.acquire_authorization_token()

        session = requests.Session()
        session.headers['Authorization'] = f'Bearer {token}'

        return session

    def acquire_authorization_token(self):
        return requests.get(
            f'https://auth.docker.io/token'
            f'?service=registry.docker.io'
            f'&scope=repository:library/{self.identity.repository}:pull'
        ).json()['token']


class GCRAuth(RemoteAuth, hosts=(
    'gcr.io',
    'asia.gcr.io',
    'eu.gcr.io',
    'us.gcr.io',
)):

    def create_session(self, auth):
        if not auth:
            return requests.Session()

        credentials = Credentials.from_service_account_file(auth).with_scopes(
            ['https://www.googleapis.com/auth/cloud-platform']
        )

        return AuthorizedSession(credentials)


class RemoteDockerImage(RemoteImage, protocol='docker'):

    def __init__(self, name, auth=None):
        self.identity = DockerIdentity.from_name(name)
        self.auth = auth

    @property
    def accept_header(self):
        # ostree currently limits itself to this v2 docker manifests
        return 'application/vnd.docker.distribution.manifest.v2+json'

    @cached_property
    def auth_service(self):
        return RemoteAuth.from_identity(self.identity)

    @cached_property
    def registry_host(self):
        return self.identity.host or 'registry-1.docker.io'

    @cached_property
    def reference(self):
        return self.identity.digest or self.identity.tag

    @cached_property
    def repository_url(self):
        # official repositories listed on docker hub have the 'library/' prefix
        if '/' in self.identity.repository:
            repository = self.identity.repository
        else:
            repository = f'library/{self.identity.repository}'

        return f'https://{self.registry_host}/v2/{repository}'

    @cached_property
    def session(self):
        session = self.auth_service.create_session(self.auth)
        session.headers['Accept'] = self.accept_header

        session.hooks = {
            'response': lambda r, **kwargs: r.raise_for_status()
        }

        return session

    @cached_property
    def manifest(self):
        url = f'{self.repository_url}/manifests/{self.reference}'
        manifest = self.session.get(url).json()

        if manifest.get('errors'):
            raise RuntimeError(manifest['errors'])

        return manifest

    def download_layer(self, layer, path):
        url = f'{self.repository_url}/blobs/{layer}'

        with self.session.get(url, stream=True) as response:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8 * 1024):
                    chunk and f.write(chunk)

    @property
    def latest_digest(self):
        url = f'{self.repository_url}/manifests/{self.reference}'
        return self.session.head(url).headers['Docker-Content-Digest']

    @property
    def layers(self):
        return tuple(l['digest'] for l in self.manifest['layers'])
