from subprocess import Popen, call, PIPE
from tempfile import NamedTemporaryFile
from typing import List

from node_launcher.command_generator import CommandGenerator
from node_launcher.constants import DARWIN, IS_WINDOWS, OPERATING_SYSTEM


def launch(command: List[str]):
    if IS_WINDOWS:
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        command[0] = '"' + command[0] + '"'
        cmd = ' '.join(command)
        with NamedTemporaryFile(suffix='-btc.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            result = Popen(
                ['start', 'powershell', '-noexit', '-windowstyle', 'hidden',
                 '-Command', f.name],
                stdin=PIPE, stdout=PIPE, stderr=PIPE,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True, shell=True)
    else:
        result = Popen(command, close_fds=True, shell=False)

    return result


def launch_terminal(command: List[str]):
    command[0] = '"' + command[0] + '"'
    cmd = ' '.join(command)
    if OPERATING_SYSTEM == DARWIN:
        with NamedTemporaryFile(suffix='-lnd.command', delete=False) as f:
            f.write(f'#!/bin/sh\n{cmd}\n'.encode('utf-8'))
            f.flush()
            call(['chmod', 'u+x', f.name])
            result = Popen(['open', '-W', f.name], close_fds=True)
    elif IS_WINDOWS:
        from subprocess import DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP
        with NamedTemporaryFile(suffix='-lnd.bat', delete=False) as f:
            f.write(cmd.encode('utf-8'))
            f.flush()
            result = Popen(
                ['start', 'powershell', '-noexit', '-Command', f.name],
                stdin=PIPE, stdout=PIPE, stderr=PIPE,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True, shell=True)
    else:
        raise NotImplementedError()
    return result


class NodeLauncher(object):
    command_generator: CommandGenerator

    def __init__(self, command_generator, launch_fn=launch,
                 launch_terminal_fn=launch_terminal):
        self.command_generator = command_generator
        self.launch = launch_fn
        self.launch_terminal = launch_terminal_fn

    def testnet_bitcoin_qt_node(self):
        result = self.launch(self.command_generator.testnet_bitcoin_qt())
        return result

    def mainnet_bitcoin_qt_node(self):
        result = self.launch(self.command_generator.mainnet_bitcoin_qt())
        return result

    def testnet_lnd_node(self):
        result = self.launch_terminal(self.command_generator.testnet_lnd())
        return result

    def mainnet_lnd_node(self):
        result = self.launch_terminal(self.command_generator.mainnet_lnd())
        return result
