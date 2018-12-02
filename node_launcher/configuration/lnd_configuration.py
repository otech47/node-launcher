import os

from node_launcher.configuration.configuration_file import ConfigurationFile
from node_launcher.constants import LND_DIR_PATH, OPERATING_SYSTEM
from node_launcher.node_software.lnd_software import LndSoftware


class LndConfiguration(object):
    file: ConfigurationFile
    software: LndSoftware

    def __init__(self, configuration_path: str = None):
        if configuration_path is None:
            configuration_path = os.path.join(LND_DIR_PATH[OPERATING_SYSTEM], 'lnd.conf')

        self.file = ConfigurationFile(configuration_path)
        self.software = LndSoftware()

        self.lnddir = LND_DIR_PATH[OPERATING_SYSTEM]
        if not os.path.exists(self.lnddir):
            os.mkdir(self.lnddir)

    def macaroon_path(self, network: str) -> str:
        macaroons_path = os.path.join(self.lnddir, 'data', 'chain', 'bitcoin', network)
        return macaroons_path

    @property
    def tls_cert_path(self) -> str:
        tls_cert_path = os.path.join(self.lnddir, 'tls.cert')
        return tls_cert_path
