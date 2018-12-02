import os

from node_launcher.configuration.configuration_file import ConfigurationFile
from node_launcher.constants import LND_DATA_PATH, OPERATING_SYSTEM
from node_launcher.node_software.lnd_software import LndSoftware


class LndConfiguration(object):
    file: ConfigurationFile
    software: LndSoftware

    def __init__(self):
        self.software = LndSoftware()

    @property
    def lnd_data_path(self) -> str:
        d = LND_DATA_PATH[OPERATING_SYSTEM]
        if not os.path.exists(d):
            os.mkdir(d)
        return d

    def macaroon_path(self, network: str) -> str:
        macaroons_path = os.path.join(self.lnd_data_path, 'data', 'chain', 'bitcoin', network)
        return macaroons_path

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnd_data_path, 'tls.cert')
        return tls_cert_path
