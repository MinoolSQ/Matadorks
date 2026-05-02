import asyncio
import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from core.pipeline_engine import PipelineEngine
from core.state_service import StateService
from core.stats import PipelineStats
from modules.scanner_service import ScannerService
from modules.validator_service import ValidatorService

@pytest.mark.asyncio
async def test_pipeline_integration_smoke():
    """
    Smoke test to verify that the PipelineEngine can orchestrate 
    multiple services and that data flows correctly between them.
    """
    test_state_file = "data/smoke_test_state.json"
    if os.path.exists(test_state_file):
        os.remove(test_state_file)

    state = StateService(state_file=test_state_file)
    stats = PipelineStats()
    engine = PipelineEngine(state=state, stats=stats)
    
    # 1. Mock Search Engine (Scanner output)
    mock_results = ["http://vulnerable-target.com/page.php?id=1", "http://safe-target.com/index.html"]
    mock_engine = AsyncMock(return_value=mock_results)
    
    # 2. Mock Validator (always success)
    # We patch the internal _validate_url to avoid aiohttp mocking complexity
    
    # Patching the components
    with patch("modules.scanner_service.get_google_pool") as mock_pool_getter, \
         patch("modules.scanner_service.GHDBProvider") as mock_ghdb, \
         patch("modules.validator_service.ValidatorService._validate_url", new_callable=AsyncMock) as mock_validate:
        
        mock_validate.return_value = True
        
        # Setup Mocks
        mock_pool = MagicMock()
        mock_pool.size.return_value = 10
        mock_pool.get_random.return_value = "http://proxy:8080"
        mock_pool_getter.return_value = mock_pool
        
        mock_ghdb_inst = MagicMock()
        mock_ghdb_inst.get_dork_map.return_value = {"test dork": "1234"}
        mock_ghdb.return_value = mock_ghdb_inst
        
        # Instantiate services
        scanner = ScannerService(stats=stats, app_state=state)
        # Override engines to use our mock
        scanner.engines = [("MockEngine", mock_engine)]
        
        validator = ValidatorService(stats=stats)
        validator.output_file = "data/smoke_validated.txt"
        
        # Add to engine
        engine.add_service(scanner)
        engine.add_service(validator)
        
        # Run pipeline with one dork
        # We wrap in a timeout to prevent hanging if something goes wrong
        try:
            await asyncio.wait_for(engine.run(["test dork"]), timeout=10)
        except asyncio.TimeoutError:
            pytest.fail("Pipeline smoke test timed out!")

        # Assertions
        assert stats.urls_scanned >= 1, "Scanner should have found URLs"
        assert stats.validated >= 1, "Validator should have validated at least one URL"
        assert state.is_processed(mock_results[0]), "State should record processed URLs"
        assert os.path.exists("data/smoke_validated.txt"), "Validator should have written to output file"

    # Cleanup
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    if os.path.exists("data/smoke_validated.txt"):
        os.remove("data/smoke_validated.txt")
