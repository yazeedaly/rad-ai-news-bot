# Radiology AI News Bot

An automated bot that aggregates and posts weekly updates about AI applications and research in Radiology to LinkedIn.

## Features

- Automatically fetches top 5 news articles about AI applications in healthcare
- Fetches top 5 news articles about AI research in Radiology
- Creates concise summaries with key takeaways
- Generates professional cover images
- Posts updates to LinkedIn automatically
- Runs every Monday at 8:00 AM ET

## Setup

1. Clone the repository
2. Create a `.env` file with the following variables:
   ```
   NEWS_API_KEY=your_news_api_key
   LINKEDIN_USERNAME=your_linkedin_username
   LINKEDIN_PASSWORD=your_linkedin_password
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure GitHub Actions secrets with the same environment variables

## Usage

The bot runs automatically every Monday at 8:00 AM ET. You can also trigger it manually through GitHub Actions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT