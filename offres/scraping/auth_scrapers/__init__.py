# offres/scraping/auth_scrapers/__init__.py
"""
Scrapers avec authentification
"""
from .authenticated_scraper import AuthenticatedScraper
from .selenium_scraper import SeleniumScraper

__all__ = ['AuthenticatedScraper', 'SeleniumScraper']