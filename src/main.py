import asyncio
from datetime import datetime
import pytz
from aggregator.news_aggregator import NewsAggregator
from image_generator import create_cover_image
from linkedin_poster import LinkedInPoster
from post_formatter import PostFormatter

async def main():
    # Initialize components
    aggregator = NewsAggregator()
    linkedin_poster = LinkedInPoster()
    post_formatter = PostFormatter()

    # Get current date in ET
    et_tz = pytz.timezone('US/Eastern')
    current_date = datetime.now(et_tz)

    try:
        # Gather news
        print("Gathering news...")
        news = await aggregator.gather_news()

        # Generate cover image
        print("Generating cover image...")
        image_path = create_cover_image(current_date)

        # Format post content
        print("Formatting post...")
        post_content = post_formatter.format_post(news, current_date)

        # Post to LinkedIn
        print("Posting to LinkedIn...")
        linkedin_poster.post(post_content, image_path)

        print("Successfully posted weekly update")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())