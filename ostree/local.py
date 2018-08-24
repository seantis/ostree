from pathlib import Path
from ostree.oci import extract_oci_layers


def ensure_folder(path):
    path.mkdir(exist_ok=True)
    return path


class Cache(object):

    def __init__(self, path):
        self.path = ensure_folder(Path(path))

    @property
    def layers(self):
        return ensure_folder(self.path / 'layers')

    def pull(self, image, destination):
        destination = Path(destination)
        destination.mkdir(exist_ok=False)

        files = []

        for layer in image.layers:
            files.append(self.layers / layer)

            if not files[-1].exists():
                image.download_layer(layer, files[-1])

        extract_oci_layers(files, destination)
