import os
from tempfile import TemporaryDirectory

import pytest

from node_launcher.constants import TARGET_LND_RELEASE
from node_launcher.node_set.lnd.lnd_software import LndSoftware


@pytest.fixture
def lnd_software():
    lnd_software = LndSoftware()
    return lnd_software


class TestLndSoftware(object):
    @pytest.mark.slow
    def test_lnd(self, lnd_software: LndSoftware):
        assert os.path.isfile(lnd_software.lnd)

    @pytest.mark.slow
    def test_lncli(self, lnd_software: LndSoftware):
        assert os.path.isfile(lnd_software.lncli)

    def test_release_version(self, lnd_software: LndSoftware):
        assert lnd_software.release_version == TARGET_LND_RELEASE

    def test_binary_name(self, lnd_software: LndSoftware):
        name = lnd_software.download_name
        assert len(name)

    def test_binary_compressed_name(self, lnd_software: LndSoftware):
        name = lnd_software.download_destination_file_name
        assert len(name)

    def test_binaries_directory(self, lnd_software: LndSoftware):
        d = lnd_software.software_directory
        assert os.path.isdir(d)

    def test_binary_directory(self, lnd_software: LndSoftware):
        d = lnd_software.version_path
        assert os.path.isdir(d)

    def test_download_url(self, lnd_software: LndSoftware):
        url = lnd_software.download_url
        assert len(url)
