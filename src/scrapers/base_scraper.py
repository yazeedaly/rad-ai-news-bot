from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time

class BaseScraper(ABC):
    def __init__(self, rate_limit=1):
        self.rate_limit = rate_limit  # Time in seconds between requests
        self.last_request = 0

    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limit"""
        now = time.time()
        time_passed = now - self.last_request
        if time_passed < self.rate_limit:
            time.sleep(self.rate_limit - time_passed)
        self.last_request = time.time()

    def _make_request(self, url, headers=None):
        """Make a rate-limited request"""
        self._respect_rate_limit()
        default_headers = {
            'User-Agent': 'RadiologyAINewsBot/1.0 (Research/Educational Purpose)'
        }
        headers = headers or default_headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response

    @abstractmethod
    def get_articles(self):
        """Get articles from the source"""
        pass

    @abstractmethod
    def extract_content(self, url):
        """Extract content from an article URL"""
        pass