from .base import RemoteImage, from_address
from .docker import RemoteDockerImage


__all__ = (
    'from_address',
    'RemoteImage',
    'RemoteDockerImage',
)
