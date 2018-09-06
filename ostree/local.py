import os

from pathlib import Path
from ostree.oci import extract_oci_layers


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path


class Cache(object):

    def __init__(self, path):
        self.path = ensure_folder(Path(path))

    @property
    def layers(self):
        return ensure_folder(self.path / 'layers')

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
