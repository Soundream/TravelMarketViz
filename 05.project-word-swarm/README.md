# PhocusWire Scraper

This script scrapes article content and dates from [PhocusWire](https://www.phocuswire.com) website.

## Features

- Scrapes articles from PhocusWire's Latest News section (pages 1-500)
- Extracts article title, date, URL, and content
- Saves data in JSON format
- Implements polite scraping with delays between requests
- Saves progress after each page

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python scrape_phocuswire.py
```

## Configuration

You can adjust the following parameters in the script:

- `start_page`: The page number to start scraping from (default: 1)
- `end_page`: The page number to end scraping at (default: 10, can be set up to 500)
- `output_dir`: The directory where scraped data will be saved

## Output

The script produces two types of output files:

1. Individual page JSON files (e.g., `phocuswire_page_1.json`)
2. A combined file with all scraped articles (`phocuswire_all_articles.json`)

Each article entry contains:
- Title
- URL
- Date
- Content (text content of the article)

## Note

This scraper is designed to be respectful of the website's resources by implementing:
- Random delays between requests
- A user agent header to identify itself
- Error handling to avoid disruption

Please use responsibly and in accordance with PhocusWire's terms of service. 