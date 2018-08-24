from io import BytesIO
from pycurl import Curl


def get(url, headers=None, encoding='utf-8'):
    buffer = BytesIO()
    get_raw(url, buffer, headers)

    return buffer.getvalue().decode(encoding)


def download(url, path, headers=None):
    with open(path, 'wb') as fp:
        get_raw(url, fp=fp, headers=headers)


def get_raw(url, fp, headers=None):
    c = Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, fp)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.FOLLOWLOCATION, True)
    c.perform()
    c.close()
