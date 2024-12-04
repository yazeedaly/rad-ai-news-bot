from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from datetime import datetime

class RSNAAIScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=3)  # More conservative rate limiting for academic site
        self.base_url = 'https://pubs.rsna.org/journal/ai'
        self.current_issue_url = 'https://pubs.rsna.org/toc/ai/current'
        self.early_view_url = 'https://pubs.rsna.org/toc/ai/0/0'
        print(f"Initialized {self.__class__.__name__} with base URL: {self.base_url}")

    async def get_articles(self):
        """Fetch articles from RSNA AI journal"""
        print(f"{self.__class__.__name__}: Starting article fetch...")
        articles = []

        try:
            # Fetch early view articles
            print("Fetching early view articles...")
            early_view_articles = await self._fetch_page_articles(self.early_view_url)
            articles.extend(early_view_articles)

            # Fetch current issue articles
            print("Fetching current issue articles...")
            current_articles = await self._fetch_page_articles(self.current_issue_url)
            articles.extend(current_articles)

            print(f"{self.__class__.__name__}: Found total of {len(articles)} articles")
            return articles[:5]  # Return top 5 most recent articles

        except Exception as e:
            print(f"{self.__class__.__name__}: Error fetching articles - {str(e)}")
            return []

    async def _fetch_page_articles(self, url):
        """Fetch articles from a specific page"""
        articles = []
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find all article items
            for article_elem in soup.find_all('div', class_='articleCitation'):
                try:
                    # Extract article details
                    title_elem = article_elem.find('div', class_='art_title')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.find('a')['href'] if title_elem.find('a') else None
                    if not link:
                        continue

                    # Make sure link is absolute
                    if not link.startswith('http'):
                        link = f"https://pubs.rsna.org{link}"

                    # Extract publication date
                    date_elem = article_elem.find('span', class_='publication-date')
                    pub_date = None
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        try:
                            pub_date = datetime.strptime(date_text, '%B %Y').strftime('%Y-%m-%d')
                        except:
                            pub_date = None

                    # Extract abstract
                    abstract_elem = article_elem.find('div', class_='hlFld-Abstract')
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''

                    articles.append({
                        'title': title,
                        'url': link,
                        'published_date': pub_date,
                        'summary': abstract,
                        'source': 'RSNA AI'
                    })

                except Exception as e:
                    print(f"Error processing article element: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error fetching page {url}: {str(e)}")

        return articles

    async def extract_content(self, url):
        """Extract content from an RSNA AI article"""
        try:
            content = await self._make_request(url)
            soup = BeautifulSoup(content, 'html.parser')

            # Find article content
            article = soup.find('div', class_='article-content')
            if not article:
                return None

            # Extract abstract and main findings
            abstract = article.find('div', class_='abstractSection')
            key_points = article.find('div', class_='keyPointsSection')
            methods = article.find('div', class_='methodsSection')

            takeaways = []

            # Add key points if available
            if key_points:
                points = key_points.find_all('li')
                for point in points[:3]:  # Limit to top 3 key points
                    text = point.get_text(strip=True)
                    if text:
                        takeaways.append(text)

            # If no key points, try to extract from methods or abstract
            if not takeaways and methods:
                takeaways.append(methods.get_text(strip=True)[:200] + '...')
            elif not takeaways and abstract:
                takeaways.append(abstract.get_text(strip=True)[:200] + '...')

            return {
                'text': article.get_text(strip=True),
                'takeaways': takeaways
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None