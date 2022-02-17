import pytest
from fs_tester import FullServiceTester

@pytest.mark.asyncio
async def test_concurrent_build_then_submit() -> None:
    num_txos = 25
    pmob_send = 0.001
    interval = 0.1
    fst = FullServiceTester()
    await fst.test_concurrent_build_and_submit(num_txos, pmob_send, interval)
    assert fst.stats["num_pass"] == num_txos

@pytest.mark.asyncio
async def test_concurrent_build_and_submit() -> None:
    num_txos = 25
    pmob_send = 0.001
    interval = 0.1
    fst = FullServiceTester()
    await fst.test_concurrent_build_and_submit(num_txos, pmob_send, interval)
    assert fst.stats["num_pass"] == num_txos
