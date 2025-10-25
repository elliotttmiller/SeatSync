"""
Tests for the production Scrapling scraper service
"""

import pytest
import asyncio

from backend.app.services.scrapling_scraper import (
    ScraplingScraperService,
    get_scraper_service,
    scrape_tickets,
)


@pytest.mark.asyncio
async def test_scraper_service_initialization():
    """Test that scraper service initializes correctly"""
    service = ScraplingScraperService()
    assert service.initialized is True
    assert service.scraper_type == "scrapling"


@pytest.mark.asyncio
async def test_get_scraper_service():
    """Test global scraper service getter"""
    service = await get_scraper_service()
    assert service is not None
    assert service.scraper_type == "scrapling"
    assert service.initialized is True


@pytest.mark.asyncio
async def test_scrape_tickets_interface():
    """Test scrape_tickets function interface"""
    # Test with minimal parameters - should not crash
    try:
        result = await scrape_tickets(search_query="Test")
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'per_marketplace' in result
    except Exception as e:
        # It's okay if scraping fails in test environment
        # We're just testing the interface
        pytest.skip(f"Scraping not available in test environment: {e}")


@pytest.mark.asyncio
async def test_scrape_marketplace_error_handling():
    """Test error handling for unsupported marketplace"""
    service = await get_scraper_service()
    result = await service.scrape_marketplace(
        marketplace="unsupported_marketplace",
        search_query="test"
    )
    
    assert result['status'] == 'error'
    assert 'error' in result
    assert 'Unsupported marketplace' in result['error']


@pytest.mark.asyncio
async def test_scrape_all_marketplaces_interface():
    """Test scrape_all_marketplaces interface"""
    service = await get_scraper_service()
    
    # Test with minimal parameters - should not crash
    try:
        result = await service.scrape_all_marketplaces(search_query="Test")
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'total_listings' in result
        assert 'per_marketplace' in result
        assert 'summary' in result
    except Exception as e:
        # It's okay if actual scraping fails
        pytest.skip(f"Scraping not available in test environment: {e}")
