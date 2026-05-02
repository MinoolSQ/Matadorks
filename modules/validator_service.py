import asyncio
from core.base_service import BaseService
from core.proxy import get_async_session
from core.config import (
    DOMAIN_BLACKLIST, VALIDATED_FILE, VALIDATOR_TIMEOUT, 
    ASYNC_CONCURRENCY_LIMIT
)

class ValidatorService(BaseService):
    """
    Independent service for URL validation and availability checking.
    Refactored from modules/validator.py following the BaseService interface.
    """
    def __init__(self, name="Validator", config=None, stats=None):
        super().__init__(name, config, stats)
        self.timeout = self.config.get("timeout", VALIDATOR_TIMEOUT)
        self.output_file = self.config.get("output_file", VALIDATED_FILE)
        self.concurrency = self.config.get("concurrency", ASYNC_CONCURRENCY_LIMIT)
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.session = None
        self._session_ctx = None

    async def initialize(self):
        """Initialize async session for HTTP requests."""
        self._session_ctx = get_async_session(timeout=self.timeout)
        self.session = await self._session_ctx.__aenter__()
        self.logger.success(f"Validator initialized with timeout {self.timeout}s.")

    def _is_blacklisted(self, url):
        url_lower = url.lower()
        if not ("?" in url and "=" in url):
            return True
        return any(item in url_lower for item in DOMAIN_BLACKLIST)

    async def _validate_url(self, url):
        """Check if URL returns a 200 OK status."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            # Try HEAD request first for efficiency
            async with self.session.head(url, headers=headers, timeout=self.timeout, allow_redirects=True) as resp:
                return resp.status == 200
        except:
            try:
                # Fallback to GET
                async with self.session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True) as resp:
                    return resp.status == 200
            except:
                return False

    async def process_item(self, item):
        """
        Validates a URL item.
        Returns the item if valid, otherwise None.
        """
        async with self.semaphore:
            url_str = item["url"] if isinstance(item, dict) else item
            
            if self._is_blacklisted(url_str):
                return None
            
            if await self._validate_url(url_str):
                # Persistence to file
                try:
                    with open(self.output_file, "a") as f:
                        f.write(url_str + "\n")
                except Exception as e:
                    self.logger.error(f"Failed to write to {self.output_file}: {e}")
                
                # Update shared stats
                if self.stats:
                    self.stats.update(validated=self.stats.validated + 1)
                
                return item
            
            return None

    async def shutdown(self):
        """Close the async session."""
        if self._session_ctx:
            await self._session_ctx.__aexit__(None, None, None)
        self.logger.info("Validator Service shutting down.")
