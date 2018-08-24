# Ostree

Pulls containers and turns them into OS trees for systemd-nspawn.

## Warning

This is alpha-quality software. Things are intended to break.

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
