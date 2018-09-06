from .base import RemoteImage
from .base import RemoteAuth

from .docker import DockerIdentity
from .docker import GCRAuth
from .docker import PublicDockerAuth
from .docker import RemoteDockerImage

__all__ = (
    'DockerIdentity',
    'GCRAuth',
    'PublicDockerAuth',
    'RemoteAuth',
    'RemoteDockerImage',
    'RemoteImage',
)
