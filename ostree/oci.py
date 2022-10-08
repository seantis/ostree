import os.path
import tarfile
import shutil


def extract_oci_layers(layers, destination):

    def is_whiteout(member):
        return os.path.basename(member.path).startswith('.wh.')

    for layer in layers:
        with tarfile.open(layer, errorlevel=0) as tar:
            # apply whiteouts to the destination
            members, whiteouts = separate(tar.getmembers(), is_whiteout)

            for whiteout in whiteouts:
                apply_whiteout(destination, whiteout.path)

            # extract files sans whiteouts
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=destination, members=members)


def separate(items, is_separate):
    a, b = [], []

    for item in items:
        if is_separate(item):
            b.append(item)
        else:
            a.append(item)

    return a, b


def apply_whiteout(destination, whiteout):
    if whiteout.endswith('.wh..wh..opq'):
        apply_opaque_whiteout(destination, whiteout)
    else:
        apply_simple_whiteout(destination, whiteout)


def apply_simple_whiteout(destination, whiteout):
    target = os.path.join(
        os.path.dirname(whiteout),
        os.path.basename(whiteout)[4:]
    )

    if not os.path.exists(target):
        return

    if os.path.isdir(target):
        shutil.rmtree(target)
    else:
        os.unlink(target)


def apply_opaque_whiteout(destination, whiteout):
    target = os.path.join(destination, os.path.dirname(whiteout))

    if not os.path.exists(target):
        return

    for root, dirs, files in os.walk(target):
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
        for f in files:
            os.unlink(os.path.join(root, f))
