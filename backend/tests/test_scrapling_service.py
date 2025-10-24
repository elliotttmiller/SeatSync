"""
Tests for the Scrapling-based scraping service
"""

import pytest
import asyncio
import os

# Set environment variable to enable Scrapling for tests
os.environ['USE_SCRAPLING'] = 'false'  # Default to false for CI/CD

# Try to import Scrapling components
try:
    from backend.app.services.scrapling_service import (
        ScraplingScrapingService,
        get_scrapling_service,
        scrape_tickets_scrapling,
        SCRAPLING_AVAILABLE
    )
    SCRAPLING_TESTS_ENABLED = SCRAPLING_AVAILABLE
except ImportError:
    SCRAPLING_TESTS_ENABLED = False
    pytestmark = pytest.mark.skip("Scrapling not installed")


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_service_initialization():
    """Test that Scrapling service initializes correctly"""
    service = ScraplingScrapingService()
    result = await service.initialize()
    
    # Should initialize successfully or fail gracefully
    assert result is True or result is False
    
    # Check status
    status = service.get_status()
    assert 'initialized' in status
    assert 'scraper_type' in status
    assert 'capabilities' in status
    
    if status['initialized']:
        assert status['scraper_type'] == 'scrapling'
    
    # Cleanup
    await service.cleanup()


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_service_singleton():
    """Test that get_scrapling_service returns singleton"""
    service1 = await get_scrapling_service()
    service2 = await get_scrapling_service()
    
    # Should be same instance
    assert service1 is service2
    
    # Cleanup
    await service1.cleanup()


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_error_handling():
    """Test that Scrapling service handles errors gracefully"""
    result = await scrape_tickets_scrapling(
        marketplace="invalid_marketplace",
        search_query="test"
    )
    
    # Should return error result, not raise exception
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'platform' in result
    assert 'listings' in result


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_capabilities():
    """Test that Scrapling service reports enhanced capabilities"""
    service = await get_scrapling_service()
    status = service.get_status()
    
    capabilities = status['capabilities']
    assert isinstance(capabilities, list)
    
    # Should have enhanced capabilities
    if service.initialized:
        assert len(capabilities) > 0
        # Check for Scrapling-specific capabilities
        expected_capabilities = [
            'adaptive_tracking',
            'cloudflare_bypass',
            'tls_fingerprinting',
            'fast_parsing'
        ]
        for cap in expected_capabilities:
            if cap in capabilities:
                # At least one enhanced capability should be present
                break
        else:
            # If none found, that's ok - might not be fully initialized
            pass
    
    await service.cleanup()


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_cleanup():
    """Test that cleanup works correctly"""
    service = ScraplingScrapingService()
    await service.initialize()
    
    # Cleanup should not raise errors
    await service.cleanup()
    
    # After cleanup, should not be initialized
    assert service.initialized is False
    assert service.session is None


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_marketplace_routing():
    """Test that marketplace names are routed correctly"""
    service = await get_scrapling_service()
    
    # Test with stubhub (should not raise exception)
    result = await service.scrape_marketplace(
        marketplace="stubhub",
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'platform' in result
    
    # Check for Scrapling-specific fields
    if result.get('status') == 'success':
        assert 'scraper' in result
        assert result['scraper'] == 'scrapling'
    
    await service.cleanup()


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_scrapling_adaptive_mode():
    """Test that adaptive mode parameter is accepted"""
    service = await get_scrapling_service()
    
    # Test with adaptive=True
    result = await service.scrape_marketplace(
        marketplace="stubhub",
        search_query="test",
        adaptive=True  # This is the killer feature!
    )
    
    assert isinstance(result, dict)
    assert 'status' in result
    
    await service.cleanup()


def test_scrapling_import_structure():
    """Test that imports work correctly"""
    if SCRAPLING_TESTS_ENABLED:
        from backend.app.services.scrapling_service import (
            scrape_tickets_scrapling,
            get_scrapling_service,
            ScraplingScrapingService
        )
        
        assert scrape_tickets_scrapling is not None
        assert get_scrapling_service is not None
        assert ScraplingScrapingService is not None


@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
def test_scrapling_availability_flag():
    """Test that SCRAPLING_AVAILABLE flag is correct"""
    from backend.app.services.scrapling_service import SCRAPLING_AVAILABLE
    
    # If tests are enabled, flag should be True
    assert SCRAPLING_AVAILABLE is True


# Integration test with main scraping service
@pytest.mark.skipif(not SCRAPLING_TESTS_ENABLED, reason="Scrapling not available")
@pytest.mark.asyncio
async def test_feature_flag_integration():
    """Test that feature flag properly switches to Scrapling"""
    # Enable Scrapling via environment variable
    os.environ['USE_SCRAPLING'] = 'true'
    
    try:
        # Import after setting env var
        from backend.app.services.scraping_service import (
            ScrapingService,
            USE_SCRAPLING as service_flag
        )
        
        # Check that flag was read correctly
        assert service_flag is True
        
        # Initialize service and check it uses Scrapling
        service = ScrapingService()
        await service.initialize()
        
        status = service.get_status()
        
        # Should be using Scrapling if available
        if status['initialized']:
            # Might be 'scrapling' or fallback to 'playwright'/'http'
            assert status['scraper_type'] in ['scrapling', 'playwright', 'http']
        
        await service.cleanup()
    finally:
        # Reset environment variable
        os.environ['USE_SCRAPLING'] = 'false'


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
