from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio

class RSNAAIScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=3)
        self.base_url = 'https://pubs.rsna.org'
        self.latest_articles_url = 'https://pubs.rsna.org/toc/ai/0/0'
        self.journal_home_url = 'https://pubs.rsna.org/journal/ai'
        print(f"Initialized {self.__class__.__name__}")

    async def get_articles(self):
        """Fetch articles from RSNA AI journal"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        articles = []

        try:
            # Fetch latest articles
            content = await self._make_request(self.latest_articles_url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find all article containers
            article_containers = soup.find_all('div', class_='item__content')
            for container in article_containers:
                try:
                    # Get title and link
                    title_elem = container.find('h5', class_='item__title')
                    if not title_elem or not title_elem.find('a'):
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.find('a')['href']
                    if not link.startswith('http'):
                        link = f"{self.base_url}{link}"

                    # Get publication date
                    date_elem = container.find('span', class_='article-date')
                    pub_date = date_elem.get_text(strip=True) if date_elem else None

                    # Get abstract
                    abstract_elem = container.find('div', class_='item__abstract')
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''

                    articles.append({
                        'title': title,
                        'url': link,
                        'published_date': pub_date,
                        'summary': abstract,
                        'source': 'RSNA AI'
                    })

                except Exception as e:
                    print(f"Error processing RSNA article: {str(e)}")
                    continue

            # If no articles found in latest, try journal home
            if not articles:
                content = await self._make_request(self.journal_home_url)
                soup = BeautifulSoup(content, 'html.parser')
                
                for article in soup.find_all('div', class_='issue-item'):
                    try:
                        title_elem = article.find('h5', class_='issue-item__title')
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        link = title_elem.find('a')['href'] if title_elem.find('a') else None
                        if not link:
                            continue

                        if not link.startswith('http'):
                            link = f"{self.base_url}{link}"

                        articles.append({
                            'title': title,
                            'url': link,
                            'published_date': None,  # Date might need different parsing
                            'summary': '',
                            'source': 'RSNA AI'
                        })

                    except Exception as e:
                        print(f"Error processing RSNA article from home: {str(e)}")
                        continue

            print(f"{self.__class__.__name__}: Found {len(articles)} articles")
            return articles[:5]  # Return top 5 articles

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    async def extract_content(self, url):
        """Extract content from an RSNA AI article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find article content
            article = soup.find('div', class_='article__content')
            if not article:
                return None

            # Extract abstract
            abstract = article.find('div', class_='article-section__abstract')
            abstract_text = abstract.get_text(strip=True) if abstract else ''

            # Extract key points
            key_points = article.find('div', class_='article-section__key-points')
            takeaways = []
            if key_points:
                points = key_points.find_all('li')
                for point in points[:3]:
                    takeaways.append(point.get_text(strip=True))
            else:
                # If no key points, use first paragraph of abstract
                if abstract_text:
                    takeaways.append(abstract_text[:200] + '...')

            return {
                'text': abstract_text,
                'takeaways': takeaways
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None