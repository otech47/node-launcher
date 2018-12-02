from tempfile import NamedTemporaryFile

import pytest

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration, LndConfiguration
from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration


@pytest.fixture
def command_generator():
    with NamedTemporaryFile(suffix='-bitcoin-mainnet.conf', delete=False) as bitcoin_mainnet_file:
        with NamedTemporaryFile(suffix='-bitcoin-testnet.conf', delete=False) as bitcoin_testnet_file:
            with NamedTemporaryFile(suffix='-lnd-mainnet.conf', delete=False) as lnd_mainnet_file:
                with NamedTemporaryFile(suffix='-lnd-testnet.conf', delete=False) as lnd_testnet_file:
                    bitcoin_mainnet_conf = BitcoinConfiguration(bitcoin_mainnet_file.name)
                    bitcoin_testnet_conf = BitcoinConfiguration(bitcoin_testnet_file.name)
                    lnd_mainnet_conf = LndConfiguration(lnd_mainnet_file.name)
                    lnd_testnet_conf = LndConfiguration(lnd_testnet_file.name)
                    command_generator = CommandGenerator(
                        mainnet_conf=Configuration('mainnet', bitcoin_mainnet_conf, lnd_mainnet_conf),
                        testnet_conf=Configuration('testnet', bitcoin_testnet_conf, lnd_testnet_conf)
                    )
    return command_generator


class TestCommandGenerator(object):
    def test_bitcoin_qt(self, command_generator):
        command = command_generator.bitcoin_qt(command_generator.mainnet)
        assert command[1].startswith('-datadir=')

    def test_testnet_bitcoin_qt(self, command_generator):
        command = command_generator.testnet_bitcoin_qt()
        assert command[-1] == '-testnet=1'

    def test_mainnet_bitcoin_qt(self, command_generator):
        command = command_generator.mainnet_bitcoin_qt()
        assert command[-1] == '-testnet=0'

    def test_testnet_lnd(self, command_generator):
        assert len(command_generator.testnet_lnd())

    def test_mainnet_lnd(self, command_generator):
        assert len(command_generator.mainnet_lnd())

    def test_testnet_lncli(self, command_generator):
        testnet_lncli = command_generator.testnet_lncli()
        assert testnet_lncli

    def test_mainnet_lncli(self, command_generator):
        mainnet_lncli = command_generator.mainnet_lncli()
        assert mainnet_lncli
