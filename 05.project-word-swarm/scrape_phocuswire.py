import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
from urllib.parse import urljoin
from pathlib import Path

class PhocusWireScraper:
    def __init__(self, start_page=1, end_page=500, output_dir="output"):
        self.base_url = "https://www.phocuswire.com"
        self.list_url_template = "https://www.phocuswire.com/Latest-News?pg={}"
        self.start_page = start_page
        self.end_page = end_page
        self.output_dir = output_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    def get_soup(self, url):
        """Get BeautifulSoup object from URL."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_date(self, article_element):
        """Extract date from article element in list view."""
        try:
            # Look for the author div which contains the date
            author_div = article_element.select_one('.author')
            if not author_div:
                return None
            
            # The date is typically the text after the author name, separated by a pipe
            # First get all text content
            text_content = author_div.get_text().strip()
            
            # Split by pipe and get the second part which should be the date
            # Example: "By Rob Gill | August 22, 2018"
            if '|' in text_content:
                date_part = text_content.split('|')[1].strip()
                return date_part
            
            # If there's no pipe, try to extract any content that looks like a date
            # This is a fallback
            return text_content
            
        except Exception as e:
            print(f"Error extracting date: {e}")
            return None
    
    def extract_article_content(self, article_url):
        """Extract content from article page."""
        soup = self.get_soup(article_url)
        if not soup:
            return None
        
        try:
            # Find the article body based on the screenshot (div with articleBody itemprop)
            article_body = soup.select_one('div[itemprop="articleBody"]')
            if not article_body:
                return None
            
            # Extract paragraphs
            paragraphs = article_body.find_all('p')
            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return content
        except Exception as e:
            print(f"Error extracting content from {article_url}: {e}")
            return None
    
    def scrape_page(self, page_num):
        """Scrape a single page of article listings."""
        url = self.list_url_template.format(page_num)
        print(f"Scraping page {page_num}: {url}")
        
        soup = self.get_soup(url)
        if not soup:
            return []
        
        articles_data = []
        
        try:
            # Find list-view section based on the first screenshot
            list_view = soup.select_one('.list-view')
            if not list_view:
                print(f"No list-view found on page {page_num}")
                return []
            
            # Find all articles in the list
            articles = list_view.select('.item')
            
            for article in articles:
                try:
                    # Extract article link
                    link_element = article.select_one('a[href]')
                    if not link_element:
                        continue
                    
                    article_href = link_element.get('href')
                    if not article_href:
                        continue
                    
                    # Create full URL
                    article_url = urljoin(self.base_url, article_href)
                    
                    # Extract date
                    date = self.extract_date(article)
                    
                    # Extract title
                    title_element = article.select_one('.title')
                    title = title_element.text.strip() if title_element else None
                    
                    print(f"Found article: {title}")
                    print(f"URL: {article_url}")
                    print(f"Date: {date}")
                    
                    # Add delay to avoid overloading the server
                    time.sleep(random.uniform(1, 3))
                    
                    # Extract content
                    content = self.extract_article_content(article_url)
                    
                    if content:
                        article_data = {
                            "title": title,
                            "url": article_url,
                            "date": date,
                            "content": content
                        }
                        articles_data.append(article_data)
                        print(f"Successfully scraped article: {title}")
                    else:
                        print(f"Failed to extract content from {article_url}")
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
                
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
        
        return articles_data
    
    def save_to_json(self, data, filename):
        """Save data to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved data to {filepath}")
    
    def run(self):
        """Run the scraper for all pages."""
        all_articles = []
        
        for page_num in range(self.start_page, self.end_page + 1):
            try:
                articles_data = self.scrape_page(page_num)
                all_articles.extend(articles_data)
                
                # Save progress after each page
                self.save_to_json(articles_data, f"phocuswire_page_{page_num}.json")
                
                # Add delay between pages
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue
        
        # Save all articles to a single file
        self.save_to_json(all_articles, "phocuswire_all_articles.json")
        print(f"Scraping completed. Total articles: {len(all_articles)}")

if __name__ == "__main__":
    # Create output directory within the current script directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    
    # You can adjust the start and end page as needed
    scraper = PhocusWireScraper(start_page=1, end_page=10, output_dir=output_dir)
    scraper.run() 