class RemoteImage(object):

    protocols = {}

    def __init_subclass__(cls, protocol, **kwargs):
        cls.protocols[protocol] = cls

        super().__init_subclass__(**kwargs)

    @classmethod
    def from_name(cls, protocol, name, auth=None):
        if protocol not in RemoteImage.protocols:
            raise NotImplementedError(f"Unknown protocol: {protocol}")

        return cls.protocols[protocol](name, auth=auth)


class RemoteAuth(object):

    hosts = {}

    def __init__(self, identity):
        self.identity = identity

    def __init_subclass__(cls, hosts, **kwargs):
        for host in hosts:
            cls.hosts[host] = cls

        super().__init_subclass__(**kwargs)

    @classmethod
    def from_identity(cls, identity):
        if identity.host not in cls.hosts:
            raise NotImplementedError(f"Unknown host: {identity.host}")

        return cls.hosts[identity.host](identity)
