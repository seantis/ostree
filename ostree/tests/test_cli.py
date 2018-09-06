import logging
import pytest
import shutil

from click.testing import CliRunner
from shlex import split
from ostree.cli import cli


def run(commandline):
    return CliRunner().invoke(cli, split(commandline), catch_exceptions=False)


@pytest.mark.parametrize('image, digest', [(
    'ubuntu:18.04',
    'sha256:b5309340de7a9a540cf6c0cba3eabdfb9c9bc5153026d37991fd0028180fc725'
), (
    'gcr.io/google-containers/etcd:3.2.24',
    'sha256:adf0009b3ea09d82fb15c7649a7436e0635cb51c74c5d58796db6c3c52713a1c'
)])
def test_digest(image, digest, caplog):
    # asking for the digest of an image we identiy *by* digest, we should
    # get the same digest back (ostree should still make a lookup though)
    caplog.set_level(logging.DEBUG, logger='urllib3')

    assert run(f'digest {image}@{digest}').output.strip() == digest
    assert 'Starting new HTTPS connection' in caplog.messages[0]


@pytest.mark.parametrize('image', (
    'ubuntu:18.04',
    'gcr.io/google-containers/etcd:3.2.24'
))
def test_pull(image, temppath):
    cache = temppath / 'cache'
    tree = temppath / 'tree'

    # pull the image
    result = run(f'pull {image} {tree} --cache={cache}')
    assert result.exit_code == 0

    # make sure there are downloaded layers
    assert sum(1 for p in (cache / 'layers').iterdir())

    # make sure the files were extracted
    assert sum(1 for p in tree.iterdir())
    assert (tree / 'bin').exists()

    # try to overwrite the image (this only works with --force)
    with pytest.raises(FileExistsError):
        result = run(f'pull {image} {tree} --cache={cache}')
        assert result.exit_code != 0

    result = run(f'pull {image} {tree} --cache={cache} --force')
    assert result.exit_code == 0


def test_purge(temppath):
    cache = temppath / 'cache'
    images = temppath / 'images'

    # pull two images with some shared layers
    run(f'pull alpine:3.8 {images}/alpine --cache={cache}')
    run(f'pull python:alpine3.8 {images}/python --cache={cache}')

    # we now have two linked files
    assert sum(1 for l in (cache / 'links').iterdir()) == 2

    # and a number of layers
    layers = sum(1 for l in (cache / 'layers').iterdir())
    assert layers

    # removing the base image should not result in any removed layers
    shutil.rmtree(images / 'alpine')
    run(f'purge --cache={cache}')

    assert sum(1 for l in (cache / 'links').iterdir()) == 1
    assert layers == sum(1 for l in (cache / 'layers').iterdir())

    # doing it the other way around howevers hould result in removed layers
    run(f'pull alpine:3.8 {images}/alpine --cache={cache}')
    shutil.rmtree(images / 'python')
    run(f'purge --cache={cache}')

    assert sum(1 for l in (cache / 'links').iterdir()) == 1
    assert layers > sum(1 for l in (cache / 'layers').iterdir())

    # removing the last image and purging the cache results in no layers
    shutil.rmtree(images / 'alpine')
    run(f'purge --cache={cache}')

    assert sum(1 for l in (cache / 'links').iterdir()) == 0
    assert sum(1 for l in (cache / 'layers').iterdir()) == 0
