from typing import List

from PySide2.QtCore import SIGNAL, QProcess, QByteArray, Qt
from PySide2.QtWidgets import QTextEdit, QLineEdit, QCompleter, QWidget
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.logging import log
from node_launcher.node_set import NodeSet


class ConsoleWidget(QWidget):
    def __init__(self, node_set: NodeSet):
        super().__init__()
        self.node_set = node_set
        self.layout = QGridLayout()

        self.output = QTextEdit()
        self.output.acceptRichText = True

        self.input = QLineEdit()
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input.setCompleter(self.completer)
        self.input.setFocus()

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

        self.connect(self.input, SIGNAL("returnPressed(void)"),
                     self.execute_user_command)

        self.connect(self.completer, SIGNAL("activated(const QString&)"),
                     self.input.clear, Qt.QueuedConnection)

        self.current_cli = 'bitcoin-cli'

    @property
    def cli(self):
        if self.current_cli == 'bitcoin-cli':
            return self.node_set.bitcoind_node.software.cli

    @property
    def cli_args(self):
        if self.current_cli == 'bitcoin-cli':
            return self.node_set.bitcoind_node.configuration.cli_args

    def execute_user_command(self):
        cmd = str(self.input.text())
        self.run_command(cmd)

    def run_command(self, cmd: str):
        log.info(
            'run_command',
            program=self.cli,
            args=self.cli_args,
            cmd=cmd
        )
        self.output.append(f'> {cmd}\n')
        self.input.clear()

        process = QProcess()
        process.setProgram(self.cli)
        process.setCurrentReadChannel(0)

        # noinspection PyUnresolvedReferences
        process.readyReadStandardError.connect(
            lambda: self.handle_error(process)
        )
        # noinspection PyUnresolvedReferences
        process.readyReadStandardOutput.connect(
            lambda: self.handle_output(process)
        )

        connect_args = list(self.cli_args)

        args = cmd.split(' ')
        if args[0] == self.cli.split('/')[-1]:
            args.pop(0)
        process.setArguments(connect_args + args)
        process.start()

    def handle_error(self, process: QProcess):
        output: QByteArray = process.readAllStandardError()
        message = output.data().decode('utf-8').strip()
        self.output.append(message)

    def handle_output(self, process: QProcess):
        output: QByteArray = process.readAllStandardOutput()
        message = output.data().decode('utf-8').strip()
        if message.startswith('{') or message.startswith('['):
            formatter = HtmlFormatter()
            formatter.noclasses = True
            formatter.linenos = False
            formatter.nobackground = True
            message = highlight(message, JsonLexer(), formatter)
            self.output.insertHtml(message)
        else:
            self.output.append(message)

        # This is just for generating the command lists in constants
        # commands = None
        # if '== Blockchain ==' in message:
        #     commands = self.parse_bitcoin_cli_commands(message)
        # elif 'lncli [global options] command [command options]' in message:
        #     commands = self.parse_lncli_commands(message)
        # if commands is not None:
        #     log.debug('commands', commands=commands)

        max_scroll = self.output.verticalScrollBar().maximum()
        self.output.verticalScrollBar().setValue(max_scroll)

    @staticmethod
    def parse_bitcoin_cli_commands(message: str):
        log.debug('parse_bitcoin_cli_commands')
        commands = []
        for line in message.split(sep='\n'):
            line = line.strip()
            if not line or line.startswith('=='):
                continue
            command = line.split()[0]
            command = command.strip()
            commands.append(command)
        return commands

    @staticmethod
    def parse_lncli_commands(message: str):
        log.debug('parse_lncli_commands')
        at_commands = False
        commands = []
        for line in message.split(sep='\n'):
            line = line.strip()
            if not at_commands:
                if 'COMMANDS:' in line:
                    at_commands = True
                    log.debug('commands line',
                              line=line)
                continue
            elif 'GLOBAL OPTIONS' in line:
                return commands
            elif line.endswith(':') or not line:
                continue

            command = line.split()[0]
            command = command.strip().replace(',', '')
            commands.append(command)
        return commands
