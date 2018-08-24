import click
import ostree.remote
import ostree.local


@click.group()
def cli():
    pass


def with_cache(fn):
    return click.option(
        '--cache', help="The cache directory",
        default='/var/cache/ostree',
        envvar='OSTREE_CACHE'
    )(fn)


@cli.command()
@click.argument("address")
@click.argument("destination")
@with_cache
def pull(address, destination, cache):
    """ Pulls an image from a registry and creates an OS tree.

    Example:

        ostree pull docker://ubuntu:18.04 /var/machines/ubuntu

    The will download and extract the image at the given address into the
    destination. If the directory already exists the command will error.

    """

    image = ostree.remote.from_address(address)

    local = ostree.local.Cache(cache)
    local.pull(image, destination)


@cli.command()
@click.argument("address")
def digest(address):
    """ Returns the latest digest of the given address.

    Note: If the digest is part of the address, then said digest is returned
    without any interaction with the remote repository.

    """

    print(ostree.remote.from_address(address).latest_digest)


@cli.command()
@with_cache
def purge(cache):
    """ Takes a cache directory and purges all layers no longer in use. """

    local = ostree.local.Cache(cache)
    local.purge()
