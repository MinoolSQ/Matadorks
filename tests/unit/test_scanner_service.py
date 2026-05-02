import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from modules.scanner_service import ScannerService

@pytest.mark.asyncio
async def test_scanner_service_logic():
    # Setup mocks
    mock_engine = AsyncMock(return_value=["http://test1.com?id=1", "http://test2.com", "http://youtube.com/watch?v=123"])
    
    with patch("modules.scanner_service.get_google_pool") as mock_pool_getter, \
         patch("modules.scanner_service.GHDBProvider") as mock_ghdb:
        
        mock_pool = MagicMock()
        mock_pool.size.return_value = 10
        mock_pool.get_random.return_value = "http://proxy:8080"
        mock_pool_getter.return_value = mock_pool
        
        mock_ghdb_inst = MagicMock()
        mock_ghdb_inst.get_dork_map.return_value = {"test dork": "1234"}
        mock_ghdb.return_value = mock_ghdb_inst
        
        service = ScannerService()
        service.engines = [("Mock", mock_engine)]
        await service.initialize()
        
        # Test processing a dork
        results = await service.process_item("test dork")
        
        assert len(results) == 2  # youtube is blacklisted
        assert results[0]["url"] == "http://test1.com?id=1"
        assert results[0]["edb_id"] == "1234"
        assert results[1]["url"] == "http://test2.com"
        
        # Test deduplication
        results_again = await service.process_item("test dork")
        assert len(results_again) == 0 # Already seen
        
        await service.shutdown()

@pytest.mark.asyncio
async def test_scanner_service_empty_results():
    mock_engine = AsyncMock(return_value=[])
    
    with patch("modules.scanner_service.get_google_pool") as mock_pool_getter, \
         patch("modules.scanner_service.GHDBProvider") as mock_ghdb:
        
        mock_pool = MagicMock()
        mock_pool.size.return_value = 100
        mock_pool_getter.return_value = mock_pool
        mock_ghdb.return_value = MagicMock()
        
        service = ScannerService()
        service.engines = [("Empty", mock_engine)]
        await service.initialize()
        
        results = await service.process_item("bad dork")
        assert results is None
        
        await service.shutdown()
