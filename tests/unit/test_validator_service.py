import asyncio
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from modules.validator_service import ValidatorService

@pytest.mark.asyncio
async def test_validator_service_logic():
    test_output = "data/test_validated.txt"
    if os.path.exists(test_output): os.remove(test_output)

    with patch("modules.validator_service.ValidatorService._validate_url", new_callable=AsyncMock) as mock_validate, \
         patch("modules.validator_service.get_async_session") as mock_session_getter:
        
        mock_session_getter.return_value = MagicMock()
        
        def side_effect(url):
            return "valid" in url
            
        mock_validate.side_effect = side_effect

        service = ValidatorService(config={"output_file": test_output})
        await service.initialize()

        # Test valid item
        res1 = await service.process_item({"url": "http://valid-target.com/page?id=1"})
        assert res1 is not None
        assert res1["url"] == "http://valid-target.com/page?id=1"

        # Test invalid item
        res2 = await service.process_item({"url": "http://invalid-target.com/page?id=1"})
        assert res2 is None

        # Test blacklisted item
        res3 = await service.process_item({"url": "http://google.com/search?q=test"})
        assert res3 is None

        assert os.path.exists(test_output)
        with open(test_output, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            assert "valid-target.com" in lines[0]

        await service.shutdown()
        if os.path.exists(test_output): os.remove(test_output)
