import os
from typing import Any, Union

import psutil

from node_launcher.configuration.configuration_file import ConfigurationFile
from node_launcher.configuration.hard_drives import HardDrives
from node_launcher.constants import BITCOIN_DATA_PATH, OPERATING_SYSTEM
from node_launcher.node_software.bitcoin_software import BitcoinSoftware
from node_launcher.utilities import get_random_password, get_zmq_port


class BitcoinConfiguration(object):
    file: ConfigurationFile
    hard_drives: HardDrives
    software: BitcoinSoftware
    zmq_block_port: int
    zmq_tx_port: int

    def __init__(self, network: str, configuration_path: str = None):
        if configuration_path is None:
            configuration_path = os.path.join(BITCOIN_DATA_PATH[OPERATING_SYSTEM],
                                              'bitcoin.conf')

        self.file = ConfigurationFile(configuration_path)
        self.hard_drives = HardDrives()
        self.software = BitcoinSoftware()
        self.network = network

        if self.file.rpcuser is None:
            self.file.rpcuser = 'default_user'

        if self.file.rpcpassword is None:
            self.file.rpcpassword = get_random_password()

        if self.file.datadir is None:
            self.autoconfigure_datadir()

        if self.file.prune is None:
            self.set_prune(self.hard_drives.should_prune(self.file.datadir, True))

        if not self.detect_zmq_ports():
            self.zmq_block_port = get_zmq_port()
            self.zmq_tx_port = get_zmq_port()

    def set_prune(self, should_prune: bool = None):
        if should_prune is None:
            should_prune = self.hard_drives.should_prune(self.file.datadir, True)
        self.file.prune = should_prune
        self.file.txindex = not should_prune

    def autoconfigure_datadir(self):
        default_datadir = BITCOIN_DATA_PATH[OPERATING_SYSTEM]
        big_drive = self.hard_drives.get_big_drive()
        default_is_big_enough = not self.hard_drives.should_prune(default_datadir, True)
        default_is_biggest = self.hard_drives.is_default_partition(big_drive)
        if default_is_big_enough or default_is_biggest:
            self.file.datadir = default_datadir
            return

        if not self.hard_drives.should_prune(big_drive.mountpoint, False):
            self.file.datadir = os.path.join(big_drive.mountpoint, 'Bitcoin')
            if not os.path.exists(self.file.datadir):
                os.mkdir(self.file.datadir)
        else:
            self.file.datadir = default_datadir

    def detect_zmq_ports(self) -> bool:
        for process in psutil.process_iter():
            if 'bitcoin' in process.name():
                for connection in process.connections():

                    print('here')
