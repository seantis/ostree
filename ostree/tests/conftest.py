import pytest

from pathlib import Path


@pytest.fixture
def temppath(tmpdir):
    yield Path(tmpdir)
