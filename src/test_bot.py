import asyncio
import os
from datetime import datetime
import pytz
from src.aggregator.news_aggregator import NewsAggregator
from src.image_generator import create_cover_image
from src.linkedin_poster import LinkedInPoster

def print_debug(message):
    """Print debug message if debug mode is enabled"""
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        print(f'[DEBUG] {message}')

async def test_news_gathering():
    """Test news gathering functionality"""
    print('\n=== Testing News Gathering ===')
    aggregator = NewsAggregator()
    
    try:
        news = await aggregator.gather_news()
        print('✓ Successfully gathered news')
        
        # Print gathered news details
        print(f'\nFound {len(news["applications"])} application articles')
        print(f'Found {len(news["research"])} research articles')
        
        # Print article details if in debug mode
        for category, articles in news.items():
            print_debug(f'\n{category.upper()} ARTICLES:')
            for i, article in enumerate(articles, 1):
                print_debug(f'{i}. {article["title"]}')
                print_debug(f'   Source: {article["source"]}')
                print_debug(f'   Relevance: {article["relevance_scores"]["combined"]:.2f}')
        
        return news
    except Exception as e:
        print(f'✗ Error gathering news: {str(e)}')
        raise

def test_image_generation():
    """Test cover image generation"""
    print('\n=== Testing Image Generation ===')
    current_date = datetime.now(pytz.timezone('US/Eastern'))
    
    try:
        image_path = create_cover_image(current_date)
        print(f'✓ Successfully generated image: {image_path}')
        return image_path
    except Exception as e:
        print(f'✗ Error generating image: {str(e)}')
        raise

def test_linkedin_connection():
    """Test LinkedIn API connection"""
    print('\n=== Testing LinkedIn Connection ===')
    poster = LinkedInPoster()
    
    try:
        poster._connect()
        print('✓ Successfully connected to LinkedIn')
    except Exception as e:
        print(f'✗ Error connecting to LinkedIn: {str(e)}')
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_news_gathering())
        print('\n✅ News gathering test completed successfully!')
    except Exception as e:
        print(f'\n❌ Test failed: {str(e)}')
        raise