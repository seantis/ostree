def from_address(address):
    protocol, image = address.split('://')

    if protocol not in RemoteImage.protocols:
        raise RuntimeError(f'Unknown protocol: {protocol}')

    return RemoteImage.protocols[protocol](image)


class RemoteImage(object):

    protocols = {}

    def __init_subclass__(cls, name, **kwargs):
        cls.protocols[name] = cls
        super().__init_subclass__(**kwargs)
