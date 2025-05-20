import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
from urllib.parse import urljoin
from pathlib import Path
import concurrent.futures
from tqdm import tqdm
import logging
import re

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PhocusWireScraper:
    def __init__(self, start_page=1, end_page=300, output_dir="output", max_workers=5, delay_min=0.5, delay_max=1.5):
        self.base_url = "https://www.phocuswire.com"
        self.list_url_template = "https://www.phocuswire.com/Latest-News?pg={}"
        self.start_page = start_page
        self.end_page = end_page
        self.output_dir = output_dir
        self.max_workers = max_workers  
        self.delay_min = delay_min      
        self.delay_max = delay_max     
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
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
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
            logger.error(f"Error extracting date: {e}")
            return None
    
    def clean_text(self, text):
        """清理文本，移除多余空格和换行符"""
        if not text:
            return ""
        
        # 替换连续的换行符为单个空格
        text = re.sub(r'\n\s*\n', ' ', text)
        
        # 替换连续的空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 删除开头和结尾的空白字符
        text = text.strip()
        
        return text
    
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
            
            # 提取所有段落并单独处理
            paragraphs = article_body.find_all('p') 
            
            # 提取每个段落的文本并清理
            clean_paragraphs = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text:  # 只添加非空段落
                    clean_paragraphs.append(text)
            
            # 使用单个换行符连接段落
            content = "\n".join(clean_paragraphs)
            
            # 最终清理整个文本
            content = self.clean_text(content)
            
            return content
        except Exception as e:
            logger.error(f"Error extracting content from {article_url}: {e}")
            return None
    
    def process_article(self, article, page_num):
        """Process a single article - for parallel execution"""
        try:
            # Extract article link
            link_element = article.select_one('a[href]')
            if not link_element:
                return None
            
            article_href = link_element.get('href')
            if not article_href:
                return None
            
            # Create full URL
            article_url = urljoin(self.base_url, article_href)
            
            # Extract date
            date = self.extract_date(article)
            
            # Extract title
            title_element = article.select_one('.title')
            title = title_element.text.strip() if title_element else None
            
            logger.debug(f"Found article: {title}")
            logger.debug(f"URL: {article_url}")
            logger.debug(f"Date: {date}")
            
            # Add short delay to avoid overloading the server
            time.sleep(random.uniform(self.delay_min, self.delay_max))
            
            # Extract content
            content = self.extract_article_content(article_url)
            
            if content:
                article_data = {
                    "title": title,
                    "url": article_url,
                    "date": date,
                    "content": content,
                    "page": page_num
                }
                logger.debug(f"Successfully scraped article: {title}")
                return article_data
            else:
                logger.warning(f"Failed to extract content from {article_url}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def scrape_page(self, page_num):
        """Scrape a single page of article listings."""
        url = self.list_url_template.format(page_num)
        logger.info(f"Scraping page {page_num}: {url}")
        
        soup = self.get_soup(url)
        if not soup:
            return []
        
        articles_data = []
        
        try:
            # Find list-view section based on the first screenshot
            list_view = soup.select_one('.list-view')
            if not list_view:
                logger.warning(f"No list-view found on page {page_num}")
                return []
            
            # Find all articles in the list
            articles = list_view.select('.item')
            
            # 使用并行处理来处理页面上的所有文章
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 创建文章处理任务
                future_to_article = {
                    executor.submit(self.process_article, article, page_num): article 
                    for article in articles
                }
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_article):
                    article_data = future.result()
                    if article_data:
                        articles_data.append(article_data)
                
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")
        
        return articles_data
    
    def save_to_json(self, data, filename):
        """Save data to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved data to {filepath}")
    
    def run(self):
        """Run the scraper for all pages."""
        all_articles = []
        start_time = time.time()
        
        # 使用tqdm创建进度条
        for page_num in tqdm(range(self.start_page, self.end_page + 1), desc="Scraping pages"):
            try:
                articles_data = self.scrape_page(page_num)
                all_articles.extend(articles_data)
                
                # Save progress after each page
                self.save_to_json(articles_data, f"phocuswire_page_{page_num}.json")
                
                # 减少页面之间的延迟
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                continue
        
        # Save all articles to a single file
        self.save_to_json(all_articles, "phocuswire_all_articles.json")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Scraping completed in {elapsed_time:.2f} seconds. Total articles: {len(all_articles)}")

if __name__ == "__main__":
    # Create output directory within the current script directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    
    # 使用更多的并行处理, 减少延迟
    scraper = PhocusWireScraper(
        start_page=600, 
        end_page=1000, 
        output_dir=output_dir,
        max_workers=8,        # 增加并行数量
        delay_min=0.3,        # 减少最小延迟
        delay_max=1.0         # 减少最大延迟
    )
    scraper.run() 