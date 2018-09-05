def from_address(address, default_protocol=None):
    if '://' in address:
        protocol, image = address.split('://')
    elif default_protocol:
        protocol = default_protocol
        image = address
    else:
        raise RuntimeError(f'No protocol given')

    if protocol not in RemoteImage.protocols:
        raise RuntimeError(f'Unknown protocol: {protocol}')

    return RemoteImage.protocols[protocol](image)


class RemoteImage(object):

    protocols = {}

    def __init_subclass__(cls, name, **kwargs):
        cls.protocols[name] = cls
        super().__init_subclass__(**kwargs)
