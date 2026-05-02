import asyncio
import pytest
from core.base_service import BaseService

class MockService(BaseService):
    async def initialize(self):
        self.initialized = True
        self.shutdown_called = False

    async def process_item(self, item):
        if item == "error":
            raise ValueError("Intentional error")
        return f"processed_{item}"

    async def shutdown(self):
        self.shutdown_called = True

@pytest.mark.asyncio
async def test_base_service_flow():
    in_q = asyncio.Queue()
    out_q = asyncio.Queue()
    service = MockService("TestService")

    # Feed data
    await in_q.put("data1")
    await in_q.put("error")
    await in_q.put("data2")
    await in_q.put(None) # EOS

    # Run service
    await service.run(in_q, out_q)

    # Verify results
    assert await out_q.get() == "processed_data1"
    assert await out_q.get() == "processed_data2"
    assert await out_q.get() is None # EOS propagation

    stats = service.get_stats()
    assert stats["processed"] == 2
    assert stats["errors"] == 1
    assert service.shutdown_called is True

@pytest.mark.asyncio
async def test_base_service_abort():
    in_q = asyncio.Queue()
    out_q = asyncio.Queue()
    abort_event = asyncio.Event()
    service = MockService("AbortService")

    await in_q.put("data1")
    abort_event.set()

    # Run service
    await service.run(in_q, out_q, abort_event=abort_event)

    # Should have stopped after check
    assert service.shutdown_called is True
    assert service.get_stats()["processed"] == 0
