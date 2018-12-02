import sys

from PySide2 import QtWidgets

from node_launcher.command_generator import CommandGenerator
from node_launcher.configuration import Configuration
from node_launcher.configuration.bitcoin_configuration import \
    BitcoinConfiguration
from node_launcher.gui.launch_widget import LaunchWidget
from node_launcher.lnd_client.lnd_client import LndClient
from node_launcher.node_launcher import NodeLauncher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    bitcoin_mainnet_conf = BitcoinConfiguration()
    bitcoin_testnet_conf = BitcoinConfiguration()
    mainnet_configuration = Configuration('testnet', bitcoin_testnet_conf)
    testnet_configuration = Configuration('mainnet', bitcoin_mainnet_conf)
    command_generator = CommandGenerator(
        testnet_conf=testnet_configuration,
        mainnet_conf=mainnet_configuration
    )
    node_launcher = NodeLauncher(command_generator)
    lnd_client = LndClient(
        testnet_conf=testnet_configuration,
        mainnet_conf=mainnet_configuration
    )
    widget = LaunchWidget(node_launcher)

    widget.show()

    sys.exit(app.exec_())
