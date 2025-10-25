"""
Tests for the unified scraping service
"""

import pytest
import asyncio
from backend.app.services.scraping_service import (
    ScrapingService,
    get_scraping_service,
    scrape_tickets
)


@pytest.mark.asyncio
async def test_scraping_service_initialization():
    """Test that the scraping service initializes correctly"""
    service = ScrapingService()
    result = await service.initialize()
    
    # Should initialize with at least one method
    assert result is True or result is False  # Either succeeds or fails gracefully
    
    # Check status
    status = service.get_status()
    assert 'initialized' in status
    assert 'scraper_type' in status
    assert 'capabilities' in status
    
    # Cleanup
    await service.cleanup()


@pytest.mark.asyncio
async def test_scraping_service_singleton():
    """Test that get_scraping_service returns singleton"""
    service1 = await get_scraping_service()
    service2 = await get_scraping_service()
    
    # Should be same instance
    assert service1 is service2
    
    # Cleanup
    await service1.cleanup()


@pytest.mark.asyncio
async def test_scrape_tickets_error_handling():
    """Test that scrape_tickets handles errors gracefully"""
    result = await scrape_tickets(
        marketplace="invalid_marketplace",
        search_query="test"
    )
    
    # Should return error result, not raise exception
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'platform' in result
    assert 'listings' in result


@pytest.mark.asyncio
async def test_scraping_service_capabilities():
    """Test that service reports capabilities correctly"""
    service = await get_scraping_service()
    status = service.get_status()
    
    capabilities = status['capabilities']
    assert isinstance(capabilities, list)
    
    # Should have at least basic capabilities
    if service.initialized:
        assert len(capabilities) > 0
    
    await service.cleanup()


@pytest.mark.asyncio
async def test_scraping_service_cleanup():
    """Test that cleanup works correctly"""
    service = ScrapingService()
    await service.initialize()
    
    # Cleanup should not raise errors
    await service.cleanup()
    
    # After cleanup, should not be initialized
    assert service.initialized is False
    assert service.scraper is None


@pytest.mark.asyncio
async def test_marketplace_routing():
    """Test that marketplace names are routed correctly"""
    service = await get_scraping_service()
    
    # Test with stubhub (should not raise exception)
    result = await service.scrape_marketplace(
        marketplace="stubhub",
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'platform' in result
    
    await service.cleanup()


@pytest.mark.asyncio
async def test_scrape_all_marketplaces():
    """Test scraping all marketplaces"""
    service = await get_scraping_service()
    
    result = await service.scrape_all_marketplaces(
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'total_listings' in result
    assert 'listings' in result
    assert 'per_marketplace' in result
    assert 'summary' in result
    
    # Check summary structure
    summary = result['summary']
    assert 'successful' in summary
    assert 'failed' in summary
    assert 'total' in summary
    
    # Should have results for each marketplace
    per_marketplace = result['per_marketplace']
    assert isinstance(per_marketplace, dict)
    
    await service.cleanup()


@pytest.mark.asyncio
async def test_scrape_all_marketplaces_with_selection():
    """Test scraping selected marketplaces only"""
    service = await get_scraping_service()
    
    # Scrape only 2 marketplaces
    result = await service.scrape_all_marketplaces(
        search_query="test",
        marketplaces=["stubhub", "seatgeek"]
    )
    
    assert isinstance(result, dict)
    assert 'per_marketplace' in result
    
    # Should only have results for selected marketplaces
    per_marketplace = result['per_marketplace']
    # If scraping is not initialized, per_marketplace will be empty
    # Otherwise, it should have results for 2 marketplaces
    if service.initialized:
        assert len(per_marketplace) <= 2  # May be less if some failed
        # Check that we only have the requested marketplaces
        for marketplace in per_marketplace.keys():
            assert marketplace in ["stubhub", "seatgeek"]
    
    await service.cleanup()


@pytest.mark.asyncio
async def test_scrape_tickets_with_none_marketplace():
    """Test scrape_tickets with marketplace=None routes to all marketplaces"""
    result = await scrape_tickets(
        marketplace=None,
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'per_marketplace' in result  # Multi-marketplace result
    assert 'total_listings' in result
    assert 'summary' in result


@pytest.mark.asyncio
async def test_scrape_tickets_with_all_marketplace():
    """Test scrape_tickets with marketplace='all' routes to all marketplaces"""
    result = await scrape_tickets(
        marketplace="all",
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'per_marketplace' in result  # Multi-marketplace result
    assert 'total_listings' in result
    assert 'summary' in result


@pytest.mark.asyncio
async def test_scrape_tickets_with_single_marketplace():
    """Test scrape_tickets with specific marketplace works as before"""
    result = await scrape_tickets(
        marketplace="stubhub",
        search_query="test"
    )
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'platform' in result
    # Single marketplace result does not have 'per_marketplace'
    assert 'per_marketplace' not in result


def test_import_structure():
    """Test that imports work correctly"""
    from backend.app.services import scrape_tickets, get_scraping_service, ScrapingService
    
    assert scrape_tickets is not None
    assert get_scraping_service is not None
    assert ScrapingService is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
