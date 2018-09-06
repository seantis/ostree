import click
import os
import ostree.local
import ostree.remote
import shutil
import sys
import tempfile


def default_cache_dir():
    if os.getuid() == 0:
        return '/var/cache/ostree'
    else:
        return os.path.expanduser('~/.cache/seantis/ostree')


def available_protocols():
    protocols = list(ostree.remote.RemoteImage.protocols.keys())
    protocols.sort()

    return protocols


def postmortem_hook(type, value, tb):
    """ Optionally used as excepthook, when post-mortem debugging is used. """

    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback
        # we are NOT in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print()

        import pdb
        pdb.post_mortem(tb)


@click.group()
@click.option(
    '--pdb/--no-pdb', 'postmortem', help="Enable post-mortem", default=False)
def cli(postmortem):

    if postmortem:
        sys.excepthook = postmortem_hook


def with_cache(fn):
    return click.option(
        '--cache',
        help="The cache directory. May be a path or the keyword 'no'",
        default=default_cache_dir()
    )(fn)


def with_auth(fn):
    return click.option(
        '--auth',
        help="A token or the path to a keyfile.",
        default=None
    )(fn)


def with_protocol(fn):
    return click.option(
        '--protocol', help="The image protocol in use (only docker for now)",
        default='docker', type=click.Choice(available_protocols())
    )(fn)


@cli.command()
@click.argument("name")
@click.argument("destination")
@click.option(
    '--force', help="Removes the destination if it exists",
    is_flag=True, default=False
)
@with_cache
@with_auth
@with_protocol
def pull(name, destination, force, cache, auth, protocol):
    """ Pulls an image from a registry and creates an OS tree.

    Example:

        ostree pull ubuntu:18.04 /var/machines/ubuntu

    The will download and extract the image with the given name into the
    destination. If the directory already exists the command will error.

    """

    if cache == 'no':
        cache = tempfile.TemporaryDirectory().name

    if force and os.path.isdir(destination):
        shutil.rmtree(destination)

    image = ostree.remote.RemoteImage.from_name(protocol, name, auth)
    local = ostree.local.Cache(cache)

    local.pull(image, destination)


@cli.command()
@click.argument("name")
@with_auth
@with_protocol
def digest(name, auth, protocol):
    """ Returns the latest digest of the given address.

    Note: If the digest is part of the address, then said digest is returned
    without any interaction with the remote repository.

    """
    image = ostree.remote.RemoteImage.from_name(protocol, name, auth)

    print(image.latest_digest)


@cli.command()
@with_cache
def purge(cache):
    """ Takes a cache directory and purges all layers no longer in use. """

    local = ostree.local.Cache(cache)
    local.purge()
