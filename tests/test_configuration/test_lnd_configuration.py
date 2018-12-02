import os

import pytest

from node_launcher.configuration.lnd_configuration import (
    LndConfiguration
)


@pytest.fixture
def lnd_configuration():
    lnd_configuration = LndConfiguration()
    return lnd_configuration


class TestDirectoryConfiguration(object):
    def test_lnd_data_path(self, lnd_configuration: LndConfiguration):
        assert os.path.isdir(lnd_configuration.lnddir)
