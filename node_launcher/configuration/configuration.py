from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration
from node_launcher.configuration.lnd_configuration import LndConfiguration
from node_launcher.configuration.port_configuration import PortConfiguration


class Configuration(object):

    bitcoin: BitcoinConfiguration
    lnd: LndConfiguration
    ports: PortConfiguration
    network: str

    def __init__(self, network: str,
                 bitcoin_configuration: BitcoinConfiguration,
                 lnd_configuration: LndConfiguration):
        self.network = network
        self.ports = PortConfiguration()
        self.lnd = lnd_configuration
        self.bitcoin = bitcoin_configuration
