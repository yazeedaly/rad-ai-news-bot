import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'news_api_key': os.getenv('NEWS_API_KEY'),
    'linkedin_username': os.getenv('LINKEDIN_USERNAME'),
    'linkedin_password': os.getenv('LINKEDIN_PASSWORD'),
    'search_terms': {
        'ai_applications': 'artificial intelligence applications healthcare',
        'radiology_ai': 'artificial intelligence radiology research'
    },
    'image_settings': {
        'width': 1200,
        'height': 630,
        'background': 'white',
        'title_font_size': 60,
        'date_font_size': 40
    }
}