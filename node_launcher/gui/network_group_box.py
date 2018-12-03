import sys

from PySide2 import QtWidgets
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QErrorMessage, QInputDialog, QLineEdit
from grpc._channel import _Rendezvous

from node_launcher.constants import LINUX, OPERATING_SYSTEM
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.image_label import ImageLabel
from node_launcher.lnd_client.lnd_client import LndClient
from node_launcher.node_launcher import NodeLauncher
from node_launcher.utilities import reveal


class NetworkGroupBox(QtWidgets.QGroupBox):
    lnd_client: LndClient
    network: str
    node_launcher: NodeLauncher

    def __init__(self, network: str, node_launcher: NodeLauncher):
        super().__init__(network)
        self.network = network
        self.node_launcher = node_launcher
        self.lnd_client = LndClient(getattr(self.node_launcher.command_generator,
                                            self.network))

        self.password_dialog = QInputDialog(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(ImageLabel(f'bitcoin-{network}.png'))
        layout.addStretch(1)

        self.error_message = QErrorMessage(self)
        if OPERATING_SYSTEM == LINUX:
            self.error_message.showMessage(
                'Linux is not supported, please submit a pull request! '
                'https://github.com/PierreRochard/node-launcher')
            sys.exit(0)

        layout.addWidget(HorizontalLine())

        # Bitcoin-Qt button
        self.bitcoin_qt_button = QtWidgets.QPushButton('Launch Bitcoin')
        bitcoin_qt_launcher = getattr(node_launcher,
                                      f'{network}_bitcoin_qt_node')
        # noinspection PyUnresolvedReferences
        self.bitcoin_qt_button.clicked.connect(bitcoin_qt_launcher)
        layout.addWidget(self.bitcoin_qt_button)

        # LND button
        self.lnd_button = QtWidgets.QPushButton('Launch LND')
        lnd_launcher = getattr(node_launcher, f'{network}_lnd_node')
        # noinspection PyUnresolvedReferences
        self.lnd_button.clicked.connect(lnd_launcher)
        layout.addWidget(self.lnd_button)

        layout.addWidget(HorizontalLine())

        # Initialize wallet button
        self.initialize_wallet_button = QtWidgets.QPushButton('Initialize Wallet')
        # noinspection PyUnresolvedReferences
        self.initialize_wallet_button.clicked.connect(self.initialize_wallet)
        layout.addWidget(self.initialize_wallet_button)

        # Unlock button
        self.unlock_wallet_button = QtWidgets.QPushButton('Unlock Wallet')
        # noinspection PyUnresolvedReferences
        self.unlock_wallet_button.clicked.connect(self.password_prompt)
        layout.addWidget(self.unlock_wallet_button)

        layout.addWidget(HorizontalLine())

        # Copy REST API URL button
        self.rest_url_copy_button = QtWidgets.QPushButton(
            'Copy LND REST Address')
        # noinspection PyUnresolvedReferences
        self.rest_url_copy_button.clicked.connect(self.copy_rest_url)
        layout.addWidget(self.rest_url_copy_button)

        # Show Macaroons button
        self.show_macaroons_button = QtWidgets.QPushButton('Show Macaroons')
        # noinspection PyUnresolvedReferences
        self.show_macaroons_button.clicked.connect(self.reveal_macaroons)
        layout.addWidget(self.show_macaroons_button)

        # Copy lncli command button
        self.lncli_copy_button = QtWidgets.QPushButton('Copy lncli Command')
        # noinspection PyUnresolvedReferences
        self.lncli_copy_button.clicked.connect(self.copy_lncli_command)
        layout.addWidget(self.lncli_copy_button)

        self.setLayout(layout)

    def reveal_macaroons(self):
        macaroons_path = getattr(self.node_launcher.command_generator,
                                 self.network).lnd.macaroon_path(self.network)
        try:
            reveal(macaroons_path)
        except (FileNotFoundError, NotADirectoryError):
            self.error_message.showMessage(f'{macaroons_path} not found')
            return

    def copy_lncli_command(self):
        command = getattr(self.node_launcher.command_generator,
                          f'{self.network}_lncli')()
        QClipboard().setText(' '.join(command))

    def copy_rest_url(self):
        rest_url = getattr(self.node_launcher.command_generator,
                           f'{self.network}_rest_url')()
        QClipboard().setText(rest_url)

    def password_prompt(self):
        password, ok = QInputDialog.getText(self.password_dialog,
                                            f'Unlock {self.network} LND Wallet',
                                            'Password',
                                            QLineEdit.Password)
        if not ok:
            return
        try:
            self.lnd_client.unlock(password)
        except _Rendezvous as e:
            self.error_message.showMessage(e._state.details)
            return

    def initialize_wallet(self):
        try:
            generate_seed_response = self.lnd_client.generate_seed()

            password, ok = QInputDialog.getText(self.password_dialog,
                                                f'Unlock {self.network} LND Wallet',
                                                'Password',
                                                QLineEdit.Password)
            if not ok:
                return

            initialize_wallet_response = self.lnd_client.initialize_wallet(
                password, generate_seed_response.cipher_seed_mnemonic)

        except _Rendezvous as e:
            self.error_message.showMessage(e._state.details)
            return
