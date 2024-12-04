import sys
import os

# Print debugging information at startup
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir()}")

try:
    import asyncio
    from datetime import datetime
    import pytz
    print("Basic imports successful")

    # Try importing our local modules
    from src.aggregator.news_aggregator import NewsAggregator
    from src.image_generator import create_cover_image
    from src.linkedin_poster import LinkedInPoster
    print("Local module imports successful")

except Exception as e:
    print(f"Import error: {str(e)}")
    raise

def print_debug(message):
    """Print debug message if debug mode is enabled"""
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        print(f'[DEBUG] {message}')

async def test_news_gathering():
    """Test news gathering functionality"""
    print('\n=== Testing News Gathering ===')
    try:
        aggregator = NewsAggregator()
        print('NewsAggregator instance created successfully')
        
        news = await aggregator.gather_news()
        print('✓ Successfully gathered news')
        
        print(f'\nFound {len(news["applications"])} application articles')
        print(f'Found {len(news["research"])} research articles')
        
        for category, articles in news.items():
            print_debug(f'\n{category.upper()} ARTICLES:')
            for i, article in enumerate(articles, 1):
                print_debug(f'{i}. {article["title"]}')
                print_debug(f'   Source: {article["source"]}')
        
        return news
    except Exception as e:
        print(f'✗ Error in news gathering: {str(e)}')
        print(f'Error type: {type(e).__name__}')
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_news_gathering())
        print('\n✅ News gathering test completed successfully!')
    except Exception as e:
        print(f'\n❌ Test failed: {str(e)}')
        sys.exit(1)