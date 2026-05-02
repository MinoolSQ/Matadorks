import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from modules.injector_service import InjectorService

@pytest.mark.asyncio
async def test_injector_service_logic():
    # Setup process mock
    mock_process = MagicMock()
    mock_process.communicate = AsyncMock()
    mock_process.kill = MagicMock()
    
    with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
        # Case 1: Vulnerable with SQLMap
        mock_process.communicate.return_value = (b"fetching back-end DBMS: MySQL\nTarget is vulnerable", b"")
        service = InjectorService()
        await service.initialize()
        
        res = await service.process_item({"url": "http://vuln.com?id=1"})
        assert res is not None
        assert res["dbms"] == "MySQL"
        assert mock_exec.call_count == 1

        # Case 2: Not vulnerable with SQLMap, Ghauri disabled in config
        mock_exec.reset_mock()
        mock_process.communicate.return_value = (b"not injectable", b"")
        service_no_ghauri = InjectorService(config={"use_ghauri_fallback": False})
        await service_no_ghauri.initialize()
        res2 = await service_no_ghauri.process_item({"url": "http://safe.com?id=1"})
        assert res2 is None
        # Should call SQLMap, and NOT fall back to Ghauri
        assert mock_exec.call_count == 1

        await service.shutdown()
        await service_no_ghauri.shutdown()

@pytest.mark.asyncio
async def test_injector_service_timeout():
    mock_process = MagicMock()
    mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
    mock_process.kill = MagicMock()
    
    with patch("asyncio.create_subprocess_exec", return_value=mock_process):
        service = InjectorService(config={"timeout": 0.1})
        await service.initialize()
        
        res = await service.process_item({"url": "http://timeout.com?id=1"})
        assert res is None
        assert mock_process.kill.called

        await service.shutdown()
