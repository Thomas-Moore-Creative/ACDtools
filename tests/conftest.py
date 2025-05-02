import socket
from pathlib import Path

import pytest

_here = Path(__file__).parent

hostname = socket.gethostname()

ON_GADI = hostname.endswith(".gadi.nci.org.au")


def pytest_configure(config):
    # Register a custom marker for Gadi-only tests
    config.addinivalue_line(
        "markers", "gadi_only: mark test as expected to fail unless run on Gadi"
    )


def pytest_collection_modifyitems(config, items):
    # Dynamically apply xfail to tests marked with @pytest.mark.gadi_only
    for item in items:
        if "gadi_only" in item.keywords and not ON_GADI:
            item.add_marker(
                pytest.mark.xfail(
                    reason="This test is expected to fail unless run on Gadi."
                )
            )
