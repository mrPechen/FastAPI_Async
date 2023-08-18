import asyncio
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def event_loop() -> Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
