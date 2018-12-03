import pytest
from PySide2.QtTest import QTest

from node_launcher.gui.seed_dialog import SeedDialog


@pytest.fixture
def seed_dialog() -> SeedDialog:
    seed_dialog = SeedDialog()
    return seed_dialog


class TestSeedDialog(object):
    def test_show(self, seed_dialog: SeedDialog):
        seed_dialog.show()

