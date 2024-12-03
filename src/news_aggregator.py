import os
import json
from datetime import datetime
from newspaper import Article
from PIL import Image, ImageDraw, ImageFont
import requests
from linkedin_api import Linkedin

class RadiologyAINewsBot:
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        self.linkedin_username = os.environ.get('LINKEDIN_USERNAME')
        self.linkedin_password = os.environ.get('LINKEDIN_PASSWORD')

    def fetch_news(self):
        """Fetch news from various sources using NewsAPI"""
        # AI Applications in general
        ai_apps_news = self._fetch_news_category("artificial intelligence applications healthcare")
        # AI Research in Radiology
        rad_ai_news = self._fetch_news_category("artificial intelligence radiology research")
        
        return ai_apps_news[:5], rad_ai_news[:5]

    def _fetch_news_category(self, query):
        """Helper method to fetch news for a specific category"""
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()['articles']

    def create_summary(self, article_url):
        """Create a summary for a single article"""
        article = Article(article_url)
        article.download()
        article.parse()
        article.nlp()
        
        # Get the main summary
        summary = article.summary.split('\n')[0]  # First paragraph
        
        # Extract key points
        takeaways = article.keywords[:3]  # Top 3 keywords as takeaways
        
        return {
            'title': article.title,
            'summary': summary,
            'takeaways': takeaways
        }

    def create_cover_image(self, date):
        """Create a cover image for the update"""
        img = Image.new('RGB', (1200, 630), color='white')
        d = ImageDraw.Draw(img)
        
        # Add title and date
        title_font = ImageFont.truetype("arial.ttf", 60)
        date_font = ImageFont.truetype("arial.ttf", 40)
        
        d.text((100, 100), "Weekly Radiology AI News Update", font=title_font, fill='black')
        d.text((100, 200), date.strftime("%B %d, %Y"), font=date_font, fill='black')
        
        # Save the image
        img_path = f"images/cover_{date.strftime('%Y%m%d')}.png"
        img.save(img_path)
        return img_path

    def format_linkedin_post(self, ai_apps_news, rad_ai_news, date):
        """Format the news into a LinkedIn post"""
        post = f"📰 Weekly Radiology AI News Update - {date.strftime('%B %d, %Y')}\n\n"
        
        post += "🔬 Top AI Applications in Healthcare:\n\n"
        for i, news in enumerate(ai_apps_news, 1):
            summary = self.create_summary(news['url'])
            post += f"{i}. {summary['title']}\n"
            post += f"{summary['summary']}\n"
            post += "Key takeaways:\n"
            for takeaway in summary['takeaways']:
                post += f"• {takeaway}\n"
            post += "\n"
        
        post += "🏥 Latest in Radiology AI Research:\n\n"
        for i, news in enumerate(rad_ai_news, 1):
            summary = self.create_summary(news['url'])
            post += f"{i}. {summary['title']}\n"
            post += f"{summary['summary']}\n"
            post += "Key takeaways:\n"
            for takeaway in summary['takeaways']:
                post += f"• {takeaway}\n"
            post += "\n"
        
        return post

    def post_to_linkedin(self, post_text, image_path):
        """Post the update to LinkedIn"""
        api = Linkedin(self.linkedin_username, self.linkedin_password)
        api.post(post_text, image_path)

    def run(self):
        """Main execution method"""
        current_date = datetime.now()
        
        # Fetch news
        ai_apps_news, rad_ai_news = self.fetch_news()
        
        # Create cover image
        image_path = self.create_cover_image(current_date)
        
        # Format post
        post_content = self.format_linkedin_post(ai_apps_news, rad_ai_news, current_date)
        
        # Post to LinkedIn
        self.post_to_linkedin(post_content, image_path)

if __name__ == "__main__":
    bot = RadiologyAINewsBot()
    bot.run()