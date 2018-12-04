import pytest
from tempfile import NamedTemporaryFile

from node_launcher.configuration import (
    Configuration,
    BitcoinConfiguration,
    LndConfiguration
)
from node_launcher.lnd_client.lnd_client import LndClient
from node_launcher.command_generator import CommandGenerator
from node_launcher.node_launcher import NodeLauncher


@pytest.fixture
def network() -> str:
    return 'testnet'


@pytest.fixture
def bitcoin_configuration() -> BitcoinConfiguration:
    bitcoin_configuration = BitcoinConfiguration(network='testnet')
    return bitcoin_configuration


@pytest.fixture
def lnd_configuration() -> LndConfiguration:
    lnd_configuration = LndConfiguration(network='testnet')
    return lnd_configuration


@pytest.fixture
def configuration(network: str,
                  bitcoin_configuration: BitcoinConfiguration,
                  lnd_configuration: LndConfiguration) -> Configuration:
    configuration = Configuration(
        network,
        bitcoin_configuration,
        lnd_configuration
    )
    return configuration


@pytest.fixture
def lnd_client(configuration: Configuration) -> LndClient:
    lnd_client = LndClient(configuration)
    return lnd_client


@pytest.fixture
def command_generator() -> CommandGenerator:
    with NamedTemporaryFile(suffix='-bitcoin-mainnet.conf', delete=False) as bitcoin_mainnet_file:
        with NamedTemporaryFile(suffix='-bitcoin-testnet.conf', delete=False) as bitcoin_testnet_file:
            with NamedTemporaryFile(suffix='-lnd-mainnet.conf', delete=False) as lnd_mainnet_file:
                with NamedTemporaryFile(suffix='-lnd-testnet.conf', delete=False) as lnd_testnet_file:
                    bitcoin_mainnet_conf = BitcoinConfiguration(network='mainnet',
                                                                configuration_path=bitcoin_mainnet_file.name)
                    bitcoin_testnet_conf = BitcoinConfiguration(network='testnet',
                                                                configuration_path=bitcoin_testnet_file.name)
                    lnd_mainnet_conf = LndConfiguration(network='mainnet',
                                                        configuration_path=lnd_mainnet_file.name)
                    lnd_testnet_conf = LndConfiguration(network='testnet',
                                                        configuration_path=lnd_testnet_file.name)
                    command_generator = CommandGenerator(
                        mainnet_conf=Configuration('mainnet', bitcoin_mainnet_conf, lnd_mainnet_conf),
                        testnet_conf=Configuration('testnet', bitcoin_testnet_conf, lnd_testnet_conf)
                    )
    return command_generator


@pytest.fixture
def node_launcher(command_generator: CommandGenerator) -> NodeLauncher:
    node_launcher = NodeLauncher(command_generator)
    return node_launcher
