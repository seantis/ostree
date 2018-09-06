# Ostree

Pulls containers and turns them into OS trees for systemd-nspawn.

You can pull a Docker container:
```bash
pip install ostree
ostree pull python:3.7-alpine ./alpine
```

And run it with systemd-nspawn:
```bash
sudo systemd-nspawn --directory ./alpine python

Spawning container alpine on /home/denis/alpine.
Press ^] three times within 1s to kill container.
Timezone UTC does not exist in container, not updating container timezone.
Python 3.7.0 (default, Aug 22 2018, 20:39:59)
[GCC 6.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## Warning

This is alpha-quality software. Things are intended to break.

## Supported Registries

The following registries are currently supported:

* Docker (public registry only)
* Google Container Registry (public, private with service account and json keyfile)

## Requirements

* POSIX
* Python 3.6+

## Run the Tests

```bash
pip install -e '.[test]'
py.test ostree
```

## Conventions

Ostree follows [PEP8](https://www.python.org/dev/peps/pep-0008/) as closely as possible. To validate it run:

```bash
pip install -e '.[test]'
flake8 ostree
```

Ostree uses [Semantic Versioning](http://semver.org/).

## License

Ostree is released under the MIT license
