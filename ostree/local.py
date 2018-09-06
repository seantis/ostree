import hashlib
import os

from itertools import chain
from ostree.oci import extract_oci_layers
from pathlib import Path


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path


def link_path(parent_folder, destination):
    name = hashlib.md5(str(destination).encode('utf-8')).hexdigest()
    return parent_folder / name


def link_write(path, destination, layers):
    with path.open('w') as f:
        f.write(f'{destination}\n')
        f.writelines('\n'.join(layers))


def link_read(path):
    with path.open('r') as f:
        destination = Path(f.readline().strip())
        layers = f.read().strip().split('\n')

    return destination, layers


class LayersLink(object):

    def __init__(self, destination, layers):
        self.destination = destination
        self.layers = layers

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            return cls(
                destination=Path(f.readline().strip()),
                layers='\n'.split(f.read().strip())
            )


class Cache(object):

    def __init__(self, path):
        self.path = ensure_folder(Path(path))

    @property
    def layers(self):
        return ensure_folder(self.path / 'layers')

    @property
    def links(self):
        return ensure_folder(self.path / 'links')

    def pull_layer(self, image, layer):
        path = self.layers / layer

        if not path.exists():
            image.download_layer(layer, path)

        return path

    def pull(self, image, destination):
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=False)

        # this seems like an obvious place to introduce threading, but note
        # that in real-world tests the difference didn't look like it was
        # worth it (even without cache, with cache there's hardly a difference)
        #
        # even if we did the docker thing and downloaded and extracted layers
        # in a pipeline we would probably not gain too much except for increase
        # in code complexity
        #
        # also note that the requests library session we use is not really
        # thread-safe, so each thread would also have to keep its own
        # connection to the server
        files = [self.pull_layer(image, layer) for layer in image.layers]
        extract_oci_layers(files, destination)

        # keep track of the layers in use
        link = link_path(self.links, destination)
        link_write(link, destination, image.layers)

    def purge(self):
        known = {}

        for path in self.links.iterdir():
            known.__setitem__(*link_read(path))

        for destination in tuple(known.keys()):
            if not destination.exists():
                link_path(self.links, destination).unlink()
                del known[destination]

        known_layers = set(chain(*known.values()))

        for layer in self.layers.iterdir():
            if layer.name not in known_layers:
                layer.unlink()
